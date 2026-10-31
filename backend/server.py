"""REST bridge to the team's hosted Odoo 20 JSON-2 API; no local data store."""

from __future__ import annotations

import hmac
import json
import os
import re
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlparse

from odoo_client import OdooAPIError, OdooJSON2Client, load_env_file

load_env_file()
ODOO = OdooJSON2Client()
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8000"))
CURRENCY = os.environ.get("CURRENCY", "INR")
APP_API_TOKEN = os.environ.get("APP_API_TOKEN", "").strip()
MAX_LIMIT = 100


def rel_id(value):
    return value[0] if isinstance(value, list) and value else None


def rel_name(value):
    return value[1] if isinstance(value, list) and len(value) > 1 else None


def rel_ids(value):
    return value if isinstance(value, list) else []


def page_args(query):
    try:
        page = max(1, int(query.get("page", ["1"])[0]))
        limit = min(MAX_LIMIT, max(1, int(query.get("limit", ["20"])[0])))
    except ValueError:
        raise ValueError("page and limit must be integers") from None
    return page, limit, (page - 1) * limit


def fields(model, names):
    available = ODOO.fields(model)
    return [name for name in names if name == "id" or name in available]


def search_read(model, domain, names, limit=20, offset=0, order=None):
    params = {"domain": domain, "fields": fields(model, names), "limit": limit, "offset": offset}
    if order:
        params["order"] = order
    return ODOO.call(model, "search_read", **params)


def read_all(model, domain, names):
    out, offset = [], 0
    while True:
        rows = search_read(model, domain, names, limit=MAX_LIMIT, offset=offset)
        out.extend(rows)
        if len(rows) < MAX_LIMIT:
            return out
        offset += len(rows)


def paged(model, domain, names, query, mapper):
    page, limit, offset = page_args(query)
    total = ODOO.call(model, "search_count", domain=domain)
    rows = search_read(model, domain, names, limit=limit, offset=offset, order="id desc")
    return {"items": [mapper(row) for row in rows], "pagination": {"page": page, "limit": limit, "total": total}}


def customer(row):
    return {"id": row.get("id"), "name": row.get("name"), "email": row.get("email") or "", "phone": row.get("phone") or "", "isCompany": bool(row.get("is_company"))}


def product(row):
    return {
        "id": row.get("id"), "name": row.get("name"),
        "productType": "SERVICE" if row.get("type") == "service" else "GOODS",
        "salesPrice": row.get("list_price", 0), "costPrice": row.get("standard_price", 0),
        "notes": row.get("description_sale") or "", "active": bool(row.get("active", True)),
        "variantIds": rel_ids(row.get("product_variant_ids")), "currency": CURRENCY,
    }


def products_with_variants(rows):
    variant_ids = sorted({variant_id for row in rows for variant_id in rel_ids(row.get("product_variant_ids"))})
    variants_by_template = {}
    if variant_ids:
        variant_rows = ODOO.call(
            "product.product", "read", ids=variant_ids,
            fields=fields("product.product", ["id", "name", "product_tmpl_id", "list_price", "standard_price", "default_code", "product_template_attribute_value_ids"]),
        )
        value_ids = sorted({value_id for variant in variant_rows for value_id in rel_ids(variant.get("product_template_attribute_value_ids"))})
        values_by_id = {}
        if value_ids:
            value_rows = ODOO.call("product.template.attribute.value", "read", ids=value_ids, fields=["id", "name"])
            values_by_id = {value["id"]: value.get("name") for value in value_rows}
        for variant in variant_rows:
            template_id = rel_id(variant.get("product_tmpl_id"))
            variants_by_template.setdefault(template_id, []).append({
                "id": variant.get("id"), "name": variant.get("name"), "salesPrice": variant.get("list_price", 0),
                "costPrice": variant.get("standard_price", 0), "sku": variant.get("default_code") or "",
                "attributes": [values_by_id[value_id] for value_id in rel_ids(variant.get("product_template_attribute_value_ids")) if value_id in values_by_id],
            })
    result = []
    for row in rows:
        item = product(row)
        item["variants"] = variants_by_template.get(row["id"], [])
        result.append(item)
    return result


def plan(row):
    count = row.get("billing_period_value") or 1
    unit = row.get("billing_period_unit") or "month"
    return {
        "id": row.get("id"), "name": row.get("name"), "billingInterval": f"{count} {unit}{'' if count == 1 else 's'}",
        "billingPeriodValue": count, "billingPeriodUnit": unit,
        "minimumQuantity": row.get("minimum_quantity"), "startsOn": row.get("date_start") or row.get("start_date"),
        "endsOn": row.get("date_end") or row.get("end_date"), "active": bool(row.get("active", True)),
    }


def subscription_status(row):
    value = str(row.get("subscription_state") or row.get("state") or "draft").lower()
    if "progress" in value or value in {"active", "sale"}:
        return "ACTIVE"
    if "pause" in value:
        return "PAUSED"
    if any(word in value for word in ("closed", "churn", "cancel", "expired")):
        return "CLOSED"
    if any(word in value for word in ("draft", "sent", "quotation", "new")):
        return "QUOTATION"
    if any(word in value for word in ("renew", "upsell")):
        return "CONFIRMED"
    return value.upper()


def monthly_equivalent(amount, count, unit):
    periods = max(float(count or 1), 1.0)
    if unit == "year":
        periods *= 12
    elif unit == "week":
        return float(amount or 0) * 52 / (periods * 12)
    return float(amount or 0) / periods


def subscriptions(rows):
    line_ids = sorted({line for row in rows for line in rel_ids(row.get("order_line"))})
    by_order = {}
    if line_ids:
        line_rows = ODOO.call("sale.order.line", "read", ids=line_ids, fields=fields("sale.order.line", ["id", "order_id", "product_id", "product_uom_qty", "price_unit", "price_subtotal", "discount"]))
        for line in line_rows:
            by_order.setdefault(rel_id(line.get("order_id")), []).append(line)
    plan_ids = sorted({rel_id(row.get("plan_id")) for row in rows if rel_id(row.get("plan_id"))})
    plans_by_id = {}
    if plan_ids:
        plan_rows = ODOO.call("sale.subscription.plan", "read", ids=plan_ids, fields=fields("sale.subscription.plan", ["id", "billing_period_value", "billing_period_unit"]))
        plans_by_id = {row["id"]: row for row in plan_rows}
    out = []
    for row in rows:
        lines = by_order.get(row["id"], [])
        recurring = float(row.get("recurring_total") or 0) or sum(float(line.get("price_subtotal") or 0) for line in lines)
        plan_row = plans_by_id.get(rel_id(row.get("plan_id")), {})
        period = plan_row.get("billing_period_value") or 1
        unit = plan_row.get("billing_period_unit") or "month"
        monthly = float(row.get("recurring_monthly") or 0)
        if not monthly:
            monthly = monthly_equivalent(recurring, period, unit)
        first = lines[0] if lines else {}
        out.append({
            "id": row.get("id"), "number": row.get("name"), "customerName": rel_name(row.get("partner_id")),
            "productName": rel_name(first.get("product_id")), "variantName": None, "planName": rel_name(row.get("plan_id")),
            "status": subscription_status(row), "billingInterval": f"{period} {unit}{'' if period == 1 else 's'}",
            "startDate": row.get("start_date"), "nextBillingDate": row.get("next_invoice_date"), "endDate": row.get("end_date"),
            "quantity": sum(float(line.get("product_uom_qty") or 0) for line in lines),
            "unitPrice": float(first.get("price_unit") or 0), "discountPercent": float(first.get("discount") or 0),
            "recurringAmount": round(recurring, 2), "monthlyRecurringRevenue": round(monthly, 2),
            "currency": CURRENCY, "autoRenew": subscription_status(row) == "ACTIVE",
        })
    return out


def subscription_domain(query):
    meta = ODOO.fields("sale.order")
    domain = [["is_subscription", "=", True]] if "is_subscription" in meta else []
    wanted = query.get("status", [""])[0].upper()
    state_field = "subscription_state" if "subscription_state" in meta else "state"
    parts = {"ACTIVE": ("progress",), "PAUSED": ("pause",), "CLOSED": ("closed", "churn", "cancel")}
    if wanted in parts and state_field in meta:
        choices = meta[state_field].get("selection") or []
        matches = [key for key, _label in choices if any(p in str(key).lower() for p in parts[wanted])]
        domain.append([state_field, "in", matches or [parts[wanted][0]]])
    elif wanted == "QUOTATION":
        domain.append(["state", "in", ["draft", "sent"]])
    return domain


def invoice_status(row):
    if row.get("state") == "draft":
        return "DRAFT"
    if row.get("state") == "cancel":
        return "CANCELLED"
    if float(row.get("amount_residual") or 0) <= 0 or row.get("payment_state") == "paid":
        return "PAID"
    if row.get("invoice_date_due") and row["invoice_date_due"] < date.today().isoformat():
        return "OVERDUE"
    return "CONFIRMED"


def invoices(query):
    model = "account.move"
    domain = [["move_type", "=", "out_invoice"]]
    status = query.get("status", [""])[0].upper()
    if status == "DRAFT":
        domain.append(["state", "=", "draft"])
    elif status == "CANCELLED":
        domain.append(["state", "=", "cancel"])
    elif status == "PAID":
        domain.append(["payment_state", "=", "paid"])
    elif status == "OVERDUE":
        domain.extend([["state", "=", "posted"], ["amount_residual", ">", 0], ["invoice_date_due", "<", date.today().isoformat()]])
    elif status in {"CONFIRMED", "OPEN"}:
        domain.extend([["state", "=", "posted"], ["amount_residual", ">", 0]])
    page_no, limit, offset = page_args(query)
    total = ODOO.call(model, "search_count", domain=domain)
    rows = search_read(model, domain, ["id", "name", "partner_id", "invoice_origin", "invoice_date", "invoice_date_due", "state", "payment_state", "amount_untaxed", "amount_tax", "amount_total", "amount_residual", "invoice_line_ids"], limit, offset, "id desc")
    line_ids = sorted({line_id for row in rows for line_id in rel_ids(row.get("invoice_line_ids"))})
    discounts = {}
    if line_ids:
        lines = ODOO.call("account.move.line", "read", ids=line_ids, fields=fields("account.move.line", ["id", "move_id", "quantity", "price_unit", "discount", "display_type"]))
        for line in lines:
            if line.get("display_type") in {"line_section", "line_note"}:
                continue
            move_id = rel_id(line.get("move_id"))
            discounts[move_id] = discounts.get(move_id, 0) + float(line.get("quantity") or 0) * float(line.get("price_unit") or 0) * float(line.get("discount") or 0) / 100
    items = []
    for row in rows:
        total_amount, due = float(row.get("amount_total") or 0), float(row.get("amount_residual") or 0)
        items.append({
            "id": row.get("id"), "number": row.get("name"), "customerName": rel_name(row.get("partner_id")),
            "subscriptionId": row.get("invoice_origin") or "", "issueDate": row.get("invoice_date"), "dueDate": row.get("invoice_date_due"),
            "status": invoice_status(row), "subtotal": round(float(row.get("amount_untaxed") or 0), 2),
            "discountAmount": round(discounts.get(row["id"], 0), 2), "taxAmount": round(float(row.get("amount_tax") or 0), 2),
            "total": round(total_amount, 2), "amountPaid": round(max(total_amount - due, 0), 2),
            "balanceDue": round(due, 2), "currency": CURRENCY,
        })
    return {"items": items, "pagination": {"page": page_no, "limit": limit, "total": total}}


def payments(query):
    model = "account.payment"
    domain = [["payment_type", "=", "inbound"], ["state", "in", ["paid", "in_process"]]]
    if query.get("from"):
        domain.append(["date", ">=", query["from"][0]])
    if query.get("to"):
        domain.append(["date", "<=", query["to"][0]])
    page_no, limit, offset = page_args(query)
    total = ODOO.call(model, "search_count", domain=domain)
    rows = search_read(model, domain, ["id", "name", "partner_id", "amount", "date", "state", "ref", "journal_id", "payment_method_line_id", "reconciled_invoice_ids"], limit, offset, "date desc, id desc")
    invoice_ids = sorted({invoice_id for row in rows for invoice_id in rel_ids(row.get("reconciled_invoice_ids"))})
    invoice_names = {}
    if invoice_ids:
        invoice_rows = ODOO.call("account.move", "read", ids=invoice_ids, fields=["id", "name"])
        invoice_names = {row["id"]: row.get("name") for row in invoice_rows}
    items = [{
        "id": row.get("id"), "invoiceId": next(iter(rel_ids(row.get("reconciled_invoice_ids"))), None),
        "invoiceNumber": next((invoice_names[i] for i in rel_ids(row.get("reconciled_invoice_ids")) if i in invoice_names), None),
        "customerName": rel_name(row.get("partner_id")), "amount": round(float(row.get("amount") or 0), 2),
        "method": rel_name(row.get("payment_method_line_id")) or rel_name(row.get("journal_id")) or "",
        "paidAt": row.get("date"), "note": row.get("ref") or row.get("name") or "", "currency": CURRENCY, "status": row.get("state"),
    } for row in rows]
    return {"items": items, "pagination": {"page": page_no, "limit": limit, "total": total}}


def dashboard_summary():
    active_domain = subscription_domain({"status": ["ACTIVE"]})
    active_rows = read_all("sale.order", active_domain, ["id", "name", "partner_id", "plan_id", "subscription_state", "state", "is_subscription", "start_date", "next_invoice_date", "end_date", "order_line", "recurring_monthly", "recurring_total"])
    active = subscriptions(active_rows)
    today = date.today()
    outstanding_rows = read_all("account.move", [["move_type", "=", "out_invoice"], ["state", "=", "posted"], ["amount_residual", ">", 0]], ["id", "amount_residual", "invoice_date_due"])
    first_month_day = today.replace(day=1).isoformat()
    collected_rows = read_all("account.payment", [["payment_type", "=", "inbound"], ["state", "in", ["paid", "in_process"]], ["date", ">=", first_month_day], ["date", "<=", today.isoformat()]], ["id", "amount"])
    overdue_rows = [row for row in outstanding_rows if row.get("invoice_date_due") and row["invoice_date_due"] < today.isoformat()]
    return {
        "currency": CURRENCY, "activeSubscriptions": len(active_rows),
        "monthlyRecurringRevenue": round(sum(row["monthlyRecurringRevenue"] for row in active), 2),
        "revenueCollectedThisMonth": round(sum(float(row.get("amount") or 0) for row in collected_rows), 2),
        "outstandingAmount": round(sum(float(row.get("amount_residual") or 0) for row in outstanding_rows), 2),
        "overdueAmount": round(sum(float(row.get("amount_residual") or 0) for row in overdue_rows), 2),
        "overdueInvoicesCount": len(overdue_rows),
    }


def find_name(model, name, names, domain=None):
    rows = search_read(model, list(domain or []) + [["name", "=", name]], names, limit=1)
    if not rows:
        raise OdooAPIError(404, f"No {model} record named {name} was found.")
    return rows[0]


def body_json(handler):
    try:
        size = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        raise ValueError("Invalid Content-Length") from None
    if size > 1_000_000:
        raise ValueError("Request body is too large")
    if not size:
        return {}
    try:
        value = json.loads(handler.rfile.read(size).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ValueError("Request body must be valid JSON") from None
    if not isinstance(value, dict):
        raise ValueError("Request body must be a JSON object")
    return value


def int_field(body, key):
    try:
        return int(body[key])
    except (KeyError, TypeError, ValueError):
        raise ValueError(f"{key} must be an integer") from None


def create_customer(body):
    name = str(body.get("name", "")).strip()
    if not name:
        raise ValueError("name is required")
    vals = {"name": name}
    for source, target in (("email", "email"), ("phone", "phone"), ("isCompany", "is_company")):
        if source in body:
            vals[target] = body[source]
    record_id = ODOO.call("res.partner", "create", vals=vals)
    return customer(ODOO.call("res.partner", "read", ids=[record_id], fields=["id", "name", "email", "phone", "is_company"])[0])


def create_product(body):
    name = str(body.get("name", "")).strip()
    if not name:
        raise ValueError("name is required")
    kind = str(body.get("productType", "SERVICE")).upper()
    if kind not in {"SERVICE", "GOODS"}:
        raise ValueError("productType must be SERVICE or GOODS")
    try:
        sales, cost = float(body.get("salesPrice", 0)), float(body.get("costPrice", 0))
    except (TypeError, ValueError):
        raise ValueError("salesPrice and costPrice must be numbers") from None
    if sales < 0 or cost < 0:
        raise ValueError("prices cannot be negative")
    vals = {"name": name, "type": "service" if kind == "SERVICE" else "consu", "list_price": sales, "standard_price": cost, "description_sale": str(body.get("notes", ""))}
    if "active" in body:
        vals["active"] = bool(body["active"])
    record_id = ODOO.call("product.template", "create", vals=vals)
    row = ODOO.call("product.template", "read", ids=[record_id], fields=fields("product.template", ["id", "name", "type", "list_price", "standard_price", "description_sale", "active", "product_variant_ids"]))[0]
    return products_with_variants([row])[0]


def create_plan(body):
    name = str(body.get("name", "")).strip()
    unit = str(body.get("billingPeriodUnit", "month")).lower().rstrip("s")
    try:
        count = int(body.get("billingPeriodValue", 1))
    except (TypeError, ValueError):
        raise ValueError("billingPeriodValue must be a positive integer") from None
    if not name or unit not in {"week", "month", "year"} or count < 1:
        raise ValueError("Provide a name and a positive billing interval in weeks, months, or years")
    meta = ODOO.fields("sale.subscription.plan")
    vals = {"name": name, "billing_period_unit": unit, "billing_period_value": count}
    for key in ("minimumQuantity", "startsOn", "endsOn"):
        model_field = {"minimumQuantity": "minimum_quantity", "startsOn": "date_start", "endsOn": "date_end"}[key]
        if key in body and model_field in meta:
            vals[model_field] = body[key]
    record_id = ODOO.call("sale.subscription.plan", "create", vals=vals)
    return plan(ODOO.call("sale.subscription.plan", "read", ids=[record_id], fields=fields("sale.subscription.plan", ["id", "name", "billing_period_value", "billing_period_unit", "minimum_quantity", "date_start", "date_end", "start_date", "end_date", "active"]))[0])


def create_subscription(body):
    customer_id, template_id, plan_id = int_field(body, "customerId"), int_field(body, "productId"), int_field(body, "planId")
    try:
        quantity, discount = float(body.get("quantity", 1)), float(body.get("discountPercent", 0))
    except (TypeError, ValueError):
        raise ValueError("quantity and discountPercent must be numbers") from None
    if quantity <= 0 or not 0 <= discount <= 100:
        raise ValueError("quantity must be positive and discountPercent must be between 0 and 100")
    plan_row = ODOO.call("sale.subscription.plan", "read", ids=[plan_id], fields=fields("sale.subscription.plan", ["id", "minimum_quantity", "date_start", "date_end", "start_date", "end_date"]))[0]
    minimum = float(plan_row.get("minimum_quantity") or 0)
    if minimum and quantity < minimum:
        raise OdooAPIError(400, f"This plan requires a minimum quantity of {minimum:g}.")
    available_from = plan_row.get("date_start") or plan_row.get("start_date")
    available_until = plan_row.get("date_end") or plan_row.get("end_date")
    if available_from and date.today().isoformat() < available_from:
        raise OdooAPIError(400, f"This plan is available from {available_from}.")
    if available_until and date.today().isoformat() > available_until:
        raise OdooAPIError(400, f"This plan was available only until {available_until}.")
    template = ODOO.call("product.template", "read", ids=[template_id], fields=["id", "product_variant_ids", "list_price"])[0]
    variants = rel_ids(template.get("product_variant_ids"))
    if not variants:
        raise OdooAPIError(400, "This product does not have a sellable variant.")
    meta = ODOO.fields("sale.order")
    required = {"partner_id", "plan_id", "order_line"}
    if not required.issubset(meta):
        raise OdooAPIError(501, "Subscription quotation fields are not available in this Odoo database.")
    line = {"product_id": variants[0], "product_uom_qty": quantity, "price_unit": float(body.get("unitPrice", template.get("list_price", 0))), "discount": discount}
    vals = {"partner_id": customer_id, "plan_id": plan_id, "order_line": [(0, 0, line)]}
    if body.get("startDate") and "start_date" in meta:
        vals["start_date"] = body["startDate"]
    order_id = ODOO.call("sale.order", "create", vals=vals)
    ODOO.call("sale.order", "action_confirm", ids=[order_id])
    row = ODOO.call("sale.order", "read", ids=[order_id], fields=fields("sale.order", ["id", "name", "partner_id", "plan_id", "subscription_state", "state", "is_subscription", "start_date", "next_invoice_date", "end_date", "order_line", "recurring_monthly", "recurring_total"]))[0]
    return subscriptions([row])[0]


def subscription_action(number, action, body):
    row = find_name("sale.order", number, ["id"], [["is_subscription", "=", True]])
    method = {"pause": "pause_subscription", "resume": "resume_subscription", "cancel": "set_close"}[action]
    args = {"ids": [row["id"]]}
    if action == "cancel":
        args.update({"close_reason_id": body.get("closeReasonId") or False, "renew": False})
    ODOO.call("sale.order", method, **args)
    row = ODOO.call("sale.order", "read", ids=[row["id"]], fields=fields("sale.order", ["id", "name", "partner_id", "plan_id", "subscription_state", "state", "is_subscription", "start_date", "next_invoice_date", "end_date", "order_line", "recurring_monthly", "recurring_total"]))[0]
    return subscriptions([row])[0]


def post_invoice(number):
    row = find_name("account.move", number, ["id", "state"], [["move_type", "=", "out_invoice"]])
    if row.get("state") != "draft":
        raise OdooAPIError(409, "Only a draft invoice can be posted.")
    ODOO.call("account.move", "action_post", ids=[row["id"]])
    return {"number": number, "status": "POSTED", "message": "Invoice posted in Odoo."}


def payment_options():
    journals = search_read("account.journal", [["type", "in", ["bank", "cash"]]], ["id", "name", "type"], 100)
    methods = search_read("account.payment.method.line", [["payment_type", "=", "inbound"]], ["id", "name", "journal_id"], 100)
    return {"journals": journals, "paymentMethods": [{"id": row["id"], "name": row["name"], "journalId": rel_id(row.get("journal_id"))} for row in methods]}


def register_payment(body):
    number = str(body.get("invoiceNumber", "")).strip()
    if not number:
        raise ValueError("invoiceNumber is required")
    try:
        amount = float(body["amount"])
    except (KeyError, TypeError, ValueError):
        raise ValueError("amount must be a number") from None
    if amount <= 0:
        raise ValueError("amount must be greater than zero")
    journal_id, method_id = int_field(body, "journalId"), int_field(body, "paymentMethodLineId")
    invoice = find_name("account.move", number, ["id", "state", "amount_residual"], [["move_type", "=", "out_invoice"]])
    if invoice.get("state") != "posted":
        raise OdooAPIError(409, "Post the invoice in Odoo before registering a payment.")
    balance = float(invoice.get("amount_residual") or 0)
    if amount > balance:
        raise OdooAPIError(409, f"Payment exceeds the remaining invoice balance of {balance:.2f}.")
    wizard_fields = ODOO.fields("account.payment.register")
    vals = {"amount": amount, "journal_id": journal_id, "payment_method_line_id": method_id}
    for name, value in (("payment_date", body.get("paidAt") or date.today().isoformat()), ("communication", body.get("note") or number)):
        if name in wizard_fields:
            vals[name] = value
    context = {"active_model": "account.move", "active_ids": [invoice["id"]]}
    wizard_id = ODOO.call("account.payment.register", "create", vals=vals, context=context)
    result = ODOO.call("account.payment.register", "action_create_payments", ids=[wizard_id], context=context)
    return {"invoiceNumber": number, "amount": round(amount, 2), "result": result, "message": "Odoo payment registration completed."}


class Handler(BaseHTTPRequestHandler):
    server_version = "BrightloopOdooBridge/1.0"

    def log_message(self, format_string, *args):
        # The request body and authorization header are never logged.
        super().log_message(format_string, *args)

    def send_json(self, status, payload):
        data = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", os.environ.get("CORS_ORIGIN", "*"))
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        if status != 204:
            self.wfile.write(data)

    def authorized(self):
        if not APP_API_TOKEN:
            return True
        supplied = self.headers.get("Authorization", "")
        if supplied.lower().startswith("bearer "):
            supplied = supplied[7:].strip()
        return hmac.compare_digest(supplied, APP_API_TOKEN)

    def do_OPTIONS(self):
        self.send_json(204, {})

    def do_GET(self):
        parsed = urlparse(self.path)
        path, query = unquote(parsed.path.rstrip("/")) or "/", parse_qs(parsed.query)
        if path == "/health":
            return self.send_json(200, {"status": "ok", "odooConfigured": ODOO.configured, "source": "odoo"})
        if not self.authorized():
            return self.send_json(401, {"error": "A valid app bearer token is required."})
        try:
            if path == "/api/v1/health/odoo":
                companies = search_read("res.company", [], ["id", "name"], 1)
                return self.send_json(200, {"status": "connected", "odooVersion": "20.0", "company": companies[0].get("name") if companies else None})
            if path == "/api/v1/dashboard/summary":
                return self.send_json(200, dashboard_summary())
            if path == "/api/v1/customers":
                return self.send_json(200, paged("res.partner", [], ["id", "name", "email", "phone", "is_company"], query, customer))
            if path == "/api/v1/products":
                data = paged("product.template", [["active", "=", True]], ["id", "name", "type", "list_price", "standard_price", "description_sale", "active", "product_variant_ids"], query, lambda row: row)
                data["items"] = products_with_variants(data["items"])
                return self.send_json(200, data)
            if path == "/api/v1/plans":
                return self.send_json(200, paged("sale.subscription.plan", [["active", "=", True]], ["id", "name", "billing_period_value", "billing_period_unit", "minimum_quantity", "date_start", "date_end", "start_date", "end_date", "active"], query, plan))
            if path == "/api/v1/subscriptions":
                domain = subscription_domain(query)
                data = paged("sale.order", domain, ["id", "name", "partner_id", "plan_id", "subscription_state", "state", "is_subscription", "start_date", "next_invoice_date", "end_date", "order_line", "recurring_monthly", "recurring_total"], query, lambda row: row)
                data["items"] = subscriptions(data["items"])
                return self.send_json(200, data)
            if path == "/api/v1/billing/due":
                as_of = query.get("asOf", [date.today().isoformat()])[0]
                try:
                    date.fromisoformat(as_of)
                except ValueError:
                    raise ValueError("asOf must be YYYY-MM-DD") from None
                domain = subscription_domain({"status": ["ACTIVE"]}) + [["next_invoice_date", "<=", as_of]]
                data = paged("sale.order", domain, ["id", "name", "partner_id", "plan_id", "subscription_state", "state", "is_subscription", "start_date", "next_invoice_date", "end_date", "order_line", "recurring_monthly", "recurring_total"], query, lambda row: row)
                data["items"] = subscriptions(data["items"])
                return self.send_json(200, data)
            if path == "/api/v1/invoices":
                return self.send_json(200, invoices(query))
            if path == "/api/v1/payments":
                return self.send_json(200, payments(query))
            if path == "/api/v1/payment-options":
                return self.send_json(200, payment_options())
            match = re.fullmatch(r"/api/v1/subscriptions/([^/]+)", path)
            if match:
                number = unquote(match.group(1))
                row = find_name("sale.order", number, ["id", "name", "partner_id", "plan_id", "subscription_state", "state", "is_subscription", "start_date", "next_invoice_date", "end_date", "order_line", "recurring_monthly", "recurring_total"], [["is_subscription", "=", True]])
                return self.send_json(200, subscriptions([row])[0])
            return self.send_json(404, {"error": "Route not found."})
        except ValueError as error:
            return self.send_json(400, {"error": str(error)})
        except OdooAPIError as error:
            return self.send_json(error.status, {"error": error.message})
        except Exception:
            return self.send_json(500, {"error": "Unexpected backend error. Check local server logs."})

    def do_POST(self):
        if not self.authorized():
            return self.send_json(401, {"error": "A valid app bearer token is required."})
        path = unquote(urlparse(self.path).path.rstrip("/")) or "/"
        try:
            body = body_json(self)
            if path == "/api/v1/customers":
                return self.send_json(201, create_customer(body))
            if path == "/api/v1/products":
                return self.send_json(201, create_product(body))
            if path == "/api/v1/plans":
                return self.send_json(201, create_plan(body))
            if path == "/api/v1/subscriptions":
                return self.send_json(201, create_subscription(body))
            if path == "/api/v1/payments":
                return self.send_json(201, register_payment(body))
            match = re.fullmatch(r"/api/v1/subscriptions/([^/]+)/(pause|resume|cancel)", path)
            if match:
                return self.send_json(200, subscription_action(unquote(match.group(1)), match.group(2), body))
            match = re.fullmatch(r"/api/v1/invoices/([^/]+)/(post|confirm)", path)
            if match:
                return self.send_json(200, post_invoice(unquote(match.group(1))))
            return self.send_json(404, {"error": "Route not found."})
        except ValueError as error:
            return self.send_json(400, {"error": str(error)})
        except OdooAPIError as error:
            return self.send_json(error.status, {"error": error.message})
        except Exception:
            return self.send_json(500, {"error": "Unexpected backend error. Check local server logs."})


def main():
    if HOST not in {"127.0.0.1", "localhost", "::1"} and not APP_API_TOKEN:
        raise SystemExit("Set APP_API_TOKEN before exposing the API beyond this computer.")
    if not ODOO.configured:
        print("Odoo key not configured. /health works; data routes will return 503.")
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Odoo-backed REST API listening at http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
