"""Small, dependency-free REST API for the hackathon subscription demo.

This local SQLite service implements the team's dashboard contract. Its demo
database is separate from Brightloop's hosted Odoo database; it does not sync
to Odoo until an Odoo connector is configured.
"""

from __future__ import annotations

import calendar
import json
import os
import re
import sqlite3
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = Path(os.environ.get("SUBSCRIPTION_DB_PATH", ROOT / "data" / "subscriptions.sqlite3"))
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8000"))
CURRENCY = "INR"


SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    product_type TEXT NOT NULL CHECK (product_type IN ('SERVICE', 'GOODS')),
    sales_price REAL NOT NULL CHECK (sales_price >= 0),
    cost_price REAL NOT NULL CHECK (cost_price >= 0),
    notes TEXT NOT NULL DEFAULT '',
    active INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS product_variants (
    id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id),
    name TEXT NOT NULL,
    price_extra REAL NOT NULL DEFAULT 0 CHECK (price_extra >= 0),
    cost_extra REAL NOT NULL DEFAULT 0 CHECK (cost_extra >= 0),
    UNIQUE(product_id, name)
);
CREATE TABLE IF NOT EXISTS plans (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    billing_interval TEXT NOT NULL CHECK (billing_interval IN ('MONTH', 'YEAR')),
    interval_count INTEGER NOT NULL DEFAULT 1 CHECK (interval_count > 0),
    minimum_quantity INTEGER NOT NULL DEFAULT 1 CHECK (minimum_quantity > 0),
    starts_on TEXT,
    ends_on TEXT,
    tax_rate REAL NOT NULL DEFAULT 0 CHECK (tax_rate >= 0 AND tax_rate <= 100),
    allow_pause INTEGER NOT NULL DEFAULT 1,
    allow_renewal INTEGER NOT NULL DEFAULT 1,
    allow_cancellation INTEGER NOT NULL DEFAULT 1,
    active INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS subscriptions (
    id INTEGER PRIMARY KEY,
    number TEXT NOT NULL UNIQUE,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    variant_id INTEGER REFERENCES product_variants(id),
    plan_id INTEGER NOT NULL REFERENCES plans(id),
    status TEXT NOT NULL CHECK (status IN ('DRAFT', 'QUOTATION', 'CONFIRMED', 'ACTIVE', 'PAUSED', 'CLOSED')),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price REAL NOT NULL CHECK (unit_price >= 0),
    discount_percent REAL NOT NULL DEFAULT 0 CHECK (discount_percent >= 0 AND discount_percent <= 100),
    start_date TEXT NOT NULL,
    next_billing_date TEXT NOT NULL,
    end_date TEXT,
    auto_renew INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY,
    number TEXT NOT NULL UNIQUE,
    subscription_id INTEGER NOT NULL REFERENCES subscriptions(id),
    billing_period_start TEXT NOT NULL,
    issue_date TEXT NOT NULL,
    due_date TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('DRAFT', 'CONFIRMED', 'PAID', 'OVERDUE', 'CANCELLED')),
    subtotal REAL NOT NULL,
    discount_amount REAL NOT NULL,
    tax_rate REAL NOT NULL,
    tax_amount REAL NOT NULL,
    total REAL NOT NULL,
    amount_paid REAL NOT NULL DEFAULT 0,
    UNIQUE(subscription_id, billing_period_start)
);
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY,
    invoice_id INTEGER NOT NULL REFERENCES invoices(id),
    amount REAL NOT NULL CHECK (amount > 0),
    method TEXT NOT NULL,
    paid_at TEXT NOT NULL,
    note TEXT NOT NULL DEFAULT ''
);
"""


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def date_string(value: date | None = None) -> str:
    return (value or date.today()).isoformat()


def add_period(value: date, interval: str, count: int = 1) -> date:
    months = count if interval == "MONTH" else 12 * count
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def seed_demo(connection: sqlite3.Connection) -> None:
    if connection.execute("SELECT COUNT(*) FROM customers").fetchone()[0]:
        return

    today = date.today()
    start = date(2026, 10, 31)
    next_bill = add_period(start, "MONTH")
    end = add_period(start, "YEAR")
    customer_id = connection.execute(
        "INSERT INTO customers(name, email, created_at) VALUES (?, ?, ?)",
        ("Sunmart Hackathon Demo", "demo@brightloop.example", date_string(today)),
    ).lastrowid
    product_id = connection.execute(
        "INSERT INTO products(name, product_type, sales_price, cost_price, notes) VALUES (?, ?, ?, ?, ?)",
        ("Brightloop Inventory", "SERVICE", 1000, 300, "Monthly inventory-management service"),
    ).lastrowid
    standard_variant = connection.execute(
        "INSERT INTO product_variants(product_id, name, price_extra, cost_extra) VALUES (?, ?, ?, ?)",
        (product_id, "Standard", 0, 0),
    ).lastrowid
    connection.execute(
        "INSERT INTO product_variants(product_id, name, price_extra, cost_extra) VALUES (?, ?, ?, ?)",
        (product_id, "Odoo", 560, 0),
    )
    plan_id = connection.execute(
        """INSERT INTO plans(name, billing_interval, interval_count, minimum_quantity,
           starts_on, ends_on, tax_rate, allow_pause, allow_renewal, allow_cancellation)
           VALUES (?, 'MONTH', 1, 1, ?, ?, 18, 1, 1, 1)""",
        ("Brightloop Monthly", date_string(start), date_string(end)),
    ).lastrowid
    subscription_id = connection.execute(
        """INSERT INTO subscriptions(number, customer_id, product_id, variant_id, plan_id,
           status, quantity, unit_price, discount_percent, start_date, next_billing_date,
           end_date, auto_renew, created_at)
           VALUES ('SUB-0001', ?, ?, ?, ?, 'ACTIVE', 10, 1000, 10, ?, ?, ?, 1, ?)""",
        (customer_id, product_id, standard_variant, plan_id, date_string(start), date_string(next_bill), date_string(end), date_string(today)),
    ).lastrowid

    subtotal = 10000.0
    discount = 1000.0
    tax = round((subtotal - discount) * 0.18, 2)
    connection.execute(
        """INSERT INTO invoices(number, subscription_id, billing_period_start, issue_date,
           due_date, status, subtotal, discount_amount, tax_rate, tax_amount, total, amount_paid)
           VALUES ('INV-0001', ?, ?, ?, ?, 'CONFIRMED', ?, ?, 18, ?, ?, 0)""",
        (subscription_id, date_string(start), date_string(start), date_string(start + timedelta(days=7)), subtotal, discount, tax, round(subtotal - discount + tax, 2)),
    )
    connection.commit()


def initialize() -> None:
    with connect() as connection:
        connection.executescript(SCHEMA)
        seed_demo(connection)


def row_dict(row: sqlite3.Row | None) -> dict | None:
    return dict(row) if row is not None else None


def subscription_record(connection: sqlite3.Connection, row: sqlite3.Row) -> dict:
    plan = connection.execute("SELECT * FROM plans WHERE id = ?", (row["plan_id"],)).fetchone()
    customer = connection.execute("SELECT name FROM customers WHERE id = ?", (row["customer_id"],)).fetchone()
    product = connection.execute("SELECT name FROM products WHERE id = ?", (row["product_id"],)).fetchone()
    variant = connection.execute("SELECT name FROM product_variants WHERE id = ?", (row["variant_id"],)).fetchone() if row["variant_id"] else None
    months = plan["interval_count"] * (12 if plan["billing_interval"] == "YEAR" else 1)
    recurring = row["unit_price"] * row["quantity"] * (1 - row["discount_percent"] / 100)
    return {
        "id": row["id"],
        "number": row["number"],
        "customerName": customer["name"],
        "productName": product["name"],
        "variantName": variant["name"] if variant else None,
        "planName": plan["name"],
        "status": row["status"],
        "billingInterval": f"{plan['interval_count']} {plan['billing_interval'].lower()}{'s' if plan['interval_count'] != 1 else ''}",
        "startDate": row["start_date"],
        "nextBillingDate": row["next_billing_date"],
        "endDate": row["end_date"],
        "quantity": row["quantity"],
        "unitPrice": round(row["unit_price"], 2),
        "discountPercent": round(row["discount_percent"], 2),
        "recurringAmount": round(recurring, 2),
        "monthlyRecurringRevenue": round(recurring / months, 2),
        "currency": CURRENCY,
        "autoRenew": bool(row["auto_renew"]),
    }


def invoice_record(connection: sqlite3.Connection, row: sqlite3.Row) -> dict:
    sub = connection.execute("SELECT number, customer_id FROM subscriptions WHERE id = ?", (row["subscription_id"],)).fetchone()
    customer = connection.execute("SELECT name FROM customers WHERE id = ?", (sub["customer_id"],)).fetchone()
    balance = round(max(row["total"] - row["amount_paid"], 0), 2)
    status = row["status"]
    if status == "CONFIRMED" and balance > 0 and row["due_date"] < date_string():
        status = "OVERDUE"
    return {
        "id": row["id"],
        "number": row["number"],
        "customerName": customer["name"],
        "subscriptionId": sub["number"],
        "issueDate": row["issue_date"],
        "dueDate": row["due_date"],
        "status": status,
        "subtotal": round(row["subtotal"], 2),
        "discountAmount": round(row["discount_amount"], 2),
        "taxAmount": round(row["tax_amount"], 2),
        "total": round(row["total"], 2),
        "amountPaid": round(row["amount_paid"], 2),
        "balanceDue": balance,
        "currency": CURRENCY,
    }


def paginated(items: list[dict], page: int, limit: int, total: int) -> dict:
    return {"items": items, "pagination": {"page": page, "limit": limit, "total": total}}


class ApiError(Exception):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message


class Handler(BaseHTTPRequestHandler):
    server_version = "BrightloopDemo/0.1"

    def log_message(self, format_string: str, *args) -> None:
        print(f"{self.address_string()} - {format_string % args}")

    def end_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.end_headers()

    def send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json(self) -> dict:
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length > 1_000_000:
                raise ApiError(413, "Request body is too large")
            payload = json.loads(self.rfile.read(length) or b"{}")
            if not isinstance(payload, dict):
                raise ApiError(400, "JSON request body must be an object")
            return payload
        except (ValueError, json.JSONDecodeError):
            raise ApiError(400, "Request body must contain valid JSON") from None

    def query(self) -> tuple[str, dict[str, list[str]]]:
        parsed = urlparse(self.path)
        return parsed.path.rstrip("/") or "/", parse_qs(parsed.query)

    def do_GET(self) -> None:
        path, query = self.query()
        try:
            with connect() as connection:
                if path == "/" or path == "/health":
                    return self.send_json(200, {"service": "Brightloop Subscription API", "status": "ok", "database": "local SQLite demo"})
                if path == "/api/v1/dashboard/summary":
                    return self.send_json(200, self.dashboard_summary(connection))
                if path == "/api/v1/subscriptions":
                    return self.list_subscriptions(connection, query)
                if path.startswith("/api/v1/subscriptions/"):
                    number = path.rsplit("/", 1)[1]
                    row = connection.execute("SELECT * FROM subscriptions WHERE number = ?", (number,)).fetchone()
                    if not row:
                        raise ApiError(404, "Subscription not found")
                    return self.send_json(200, subscription_record(connection, row))
                if path == "/api/v1/invoices":
                    return self.list_invoices(connection, query)
                if path == "/api/v1/payments":
                    return self.list_payments(connection, query)
                if path == "/api/v1/customers":
                    rows = connection.execute("SELECT id, name, email, created_at AS createdAt FROM customers ORDER BY name").fetchall()
                    return self.send_json(200, {"items": [dict(row) for row in rows]})
                if path == "/api/v1/products":
                    rows = connection.execute("SELECT * FROM products WHERE active = 1 ORDER BY name").fetchall()
                    products = []
                    for row in rows:
                        item = dict(row)
                        item["salesPrice"] = item.pop("sales_price")
                        item["costPrice"] = item.pop("cost_price")
                        item["productType"] = item.pop("product_type")
                        item["variants"] = [dict(variant) for variant in connection.execute("SELECT id, name, price_extra AS priceExtra, cost_extra AS costExtra FROM product_variants WHERE product_id = ? ORDER BY id", (row["id"],)).fetchall()]
                        products.append(item)
                    return self.send_json(200, {"items": products})
                if path == "/api/v1/plans":
                    rows = connection.execute("SELECT * FROM plans WHERE active = 1 ORDER BY name").fetchall()
                    return self.send_json(200, {"items": [self.plan_json(row) for row in rows]})
            raise ApiError(404, "Endpoint not found")
        except ApiError as error:
            self.send_json(error.status, {"error": error.message})
        except sqlite3.Error as error:
            self.send_json(500, {"error": "Database error", "details": str(error)})

    def do_POST(self) -> None:
        path, _query = self.query()
        try:
            data = self.read_json()
            with connect() as connection:
                if path == "/api/v1/subscriptions":
                    return self.create_subscription(connection, data)
                if path == "/api/v1/products":
                    return self.create_product(connection, data)
                if path == "/api/v1/plans":
                    return self.create_plan(connection, data)
                if path == "/api/v1/billing/run":
                    return self.run_billing(connection, data)
                if path == "/api/v1/payments":
                    return self.create_payment(connection, data)
                if path == "/api/v1/customers":
                    return self.create_customer(connection, data)
                match = re.fullmatch(r"/api/v1/invoices/([^/]+)/confirm", path)
                if match:
                    return self.confirm_invoice(connection, match.group(1))
                match = re.fullmatch(r"/api/v1/subscriptions/([^/]+)/(pause|resume|renew|cancel)", path)
                if match:
                    return self.subscription_action(connection, match.group(1), match.group(2))
            raise ApiError(404, "Endpoint not found")
        except ApiError as error:
            self.send_json(error.status, {"error": error.message})
        except sqlite3.IntegrityError as error:
            self.send_json(409, {"error": "Record conflicts with existing data", "details": str(error)})
        except sqlite3.Error as error:
            self.send_json(500, {"error": "Database error", "details": str(error)})

    def page_args(self, query: dict[str, list[str]]) -> tuple[int, int]:
        try:
            page = max(1, int(query.get("page", ["1"])[0]))
            limit = min(100, max(1, int(query.get("limit", ["20"])[0])))
            return page, limit
        except ValueError:
            raise ApiError(400, "page and limit must be integers") from None

    def dashboard_summary(self, connection: sqlite3.Connection) -> dict:
        active = connection.execute("SELECT * FROM subscriptions WHERE status = 'ACTIVE'").fetchall()
        mrr = sum(subscription_record(connection, row)["monthlyRecurringRevenue"] for row in active)
        today = date.today()
        month_start = today.replace(day=1).isoformat()
        month_end = date_string(today)
        collected = connection.execute("SELECT COALESCE(SUM(amount), 0) FROM payments WHERE paid_at BETWEEN ? AND ?", (month_start, month_end)).fetchone()[0]
        invoices = connection.execute("SELECT * FROM invoices WHERE status IN ('CONFIRMED', 'OVERDUE')").fetchall()
        open_rows = [invoice_record(connection, row) for row in invoices]
        outstanding = sum(item["balanceDue"] for item in open_rows if item["status"] in ("CONFIRMED", "OVERDUE"))
        overdue = [item for item in open_rows if item["status"] == "OVERDUE"]
        return {
            "currency": CURRENCY,
            "activeSubscriptions": len(active),
            "monthlyRecurringRevenue": round(mrr, 2),
            "revenueCollectedThisMonth": round(collected, 2),
            "outstandingAmount": round(outstanding, 2),
            "overdueAmount": round(sum(item["balanceDue"] for item in overdue), 2),
            "overdueInvoicesCount": len(overdue),
        }

    def list_subscriptions(self, connection: sqlite3.Connection, query: dict[str, list[str]]) -> None:
        page, limit = self.page_args(query)
        status = query.get("status", [None])[0]
        where = " WHERE status = ?" if status else ""
        args = (status,) if status else ()
        total = connection.execute(f"SELECT COUNT(*) FROM subscriptions{where}", args).fetchone()[0]
        rows = connection.execute(f"SELECT * FROM subscriptions{where} ORDER BY id DESC LIMIT ? OFFSET ?", (*args, limit, (page - 1) * limit)).fetchall()
        self.send_json(200, paginated([subscription_record(connection, row) for row in rows], page, limit, total))

    def list_invoices(self, connection: sqlite3.Connection, query: dict[str, list[str]]) -> None:
        page, limit = self.page_args(query)
        rows = connection.execute("SELECT * FROM invoices ORDER BY issue_date DESC, id DESC").fetchall()
        items = [invoice_record(connection, row) for row in rows]
        status = query.get("status", [None])[0]
        if status:
            items = [item for item in items if item["status"] == status]
        total = len(items)
        offset = (page - 1) * limit
        self.send_json(200, paginated(items[offset:offset + limit], page, limit, total))

    def list_payments(self, connection: sqlite3.Connection, query: dict[str, list[str]]) -> None:
        page, limit = self.page_args(query)
        start = query.get("from", [None])[0]
        end = query.get("to", [None])[0]
        where = []
        args: list[str] = []
        if start:
            where.append("p.paid_at >= ?")
            args.append(start)
        if end:
            where.append("p.paid_at <= ?")
            args.append(end)
        clause = " WHERE " + " AND ".join(where) if where else ""
        total = connection.execute(f"SELECT COUNT(*) FROM payments p{clause}", args).fetchone()[0]
        rows = connection.execute(
            f"""SELECT p.*, i.number AS invoice_number, s.customer_id, c.name AS customer_name
                FROM payments p JOIN invoices i ON i.id = p.invoice_id
                JOIN subscriptions s ON s.id = i.subscription_id
                JOIN customers c ON c.id = s.customer_id{clause}
                ORDER BY p.paid_at DESC, p.id DESC LIMIT ? OFFSET ?""",
            (*args, limit, (page - 1) * limit),
        ).fetchall()
        items = [{
            "id": row["id"], "invoiceId": row["invoice_id"], "invoiceNumber": row["invoice_number"],
            "customerName": row["customer_name"], "amount": round(row["amount"], 2),
            "method": row["method"], "paidAt": row["paid_at"], "note": row["note"], "currency": CURRENCY,
        } for row in rows]
        self.send_json(200, paginated(items, page, limit, total))

    def plan_json(self, row: sqlite3.Row) -> dict:
        return {
            "id": row["id"], "name": row["name"], "billingInterval": row["billing_interval"],
            "intervalCount": row["interval_count"], "minimumQuantity": row["minimum_quantity"],
            "startsOn": row["starts_on"], "endsOn": row["ends_on"], "taxRate": row["tax_rate"],
            "allowPause": bool(row["allow_pause"]), "allowRenewal": bool(row["allow_renewal"]),
            "allowCancellation": bool(row["allow_cancellation"]),
        }

    def create_product(self, connection: sqlite3.Connection, data: dict) -> None:
        name = self.required_text(data, "name")
        product_type = str(data.get("productType", "SERVICE")).upper()
        if product_type not in ("SERVICE", "GOODS"):
            raise ApiError(400, "productType must be SERVICE or GOODS")
        sales_price = self.number(data, "salesPrice", minimum=0)
        cost_price = self.number(data, "costPrice", minimum=0, default=0)
        cursor = connection.execute(
            "INSERT INTO products(name, product_type, sales_price, cost_price, notes) VALUES (?, ?, ?, ?, ?)",
            (name, product_type, sales_price, cost_price, str(data.get("notes", ""))),
        )
        product_id = cursor.lastrowid
        variants = data.get("variants", [])
        if not isinstance(variants, list):
            raise ApiError(400, "variants must be a list")
        for variant in variants:
            if not isinstance(variant, dict) or not variant.get("name"):
                raise ApiError(400, "Each variant needs a name")
            connection.execute(
                "INSERT INTO product_variants(product_id, name, price_extra, cost_extra) VALUES (?, ?, ?, ?)",
                (product_id, variant["name"], float(variant.get("priceExtra", 0)), float(variant.get("costExtra", 0))),
            )
        connection.commit()
        self.send_json(201, {"id": product_id, "name": name, "productType": product_type, "salesPrice": sales_price, "costPrice": cost_price, "variants": variants})

    def create_customer(self, connection: sqlite3.Connection, data: dict) -> None:
        name = self.required_text(data, "name")
        email = self.required_text(data, "email").lower()
        if "@" not in email:
            raise ApiError(400, "email must be a valid email address")
        cursor = connection.execute(
            "INSERT INTO customers(name, email, created_at) VALUES (?, ?, ?)",
            (name, email, date_string()),
        )
        connection.commit()
        self.send_json(201, {"id": cursor.lastrowid, "name": name, "email": email, "createdAt": date_string()})

    def create_plan(self, connection: sqlite3.Connection, data: dict) -> None:
        name = self.required_text(data, "name")
        interval = str(data.get("billingInterval", "MONTH")).upper()
        if interval not in ("MONTH", "YEAR"):
            raise ApiError(400, "billingInterval must be MONTH or YEAR")
        try:
            count = int(data.get("intervalCount", 1))
            minimum = int(data.get("minimumQuantity", 1))
        except (ValueError, TypeError):
            raise ApiError(400, "intervalCount and minimumQuantity must be integers") from None
        if count < 1 or minimum < 1:
            raise ApiError(400, "intervalCount and minimumQuantity must be at least 1")
        tax_rate = self.number(data, "taxRate", minimum=0, maximum=100, default=0)
        cursor = connection.execute(
            """INSERT INTO plans(name, billing_interval, interval_count, minimum_quantity, starts_on,
               ends_on, tax_rate, allow_pause, allow_renewal, allow_cancellation)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (name, interval, count, minimum, data.get("startsOn"), data.get("endsOn"), tax_rate,
             int(bool(data.get("allowPause", True))), int(bool(data.get("allowRenewal", True))), int(bool(data.get("allowCancellation", True)))),
        )
        connection.commit()
        row = connection.execute("SELECT * FROM plans WHERE id = ?", (cursor.lastrowid,)).fetchone()
        self.send_json(201, self.plan_json(row))

    def create_subscription(self, connection: sqlite3.Connection, data: dict) -> None:
        try:
            customer_id = int(data["customerId"])
            product_id = int(data["productId"])
            plan_id = int(data["planId"])
            quantity = int(data.get("quantity", 1))
        except (KeyError, ValueError, TypeError):
            raise ApiError(400, "customerId, productId, and planId are required integers") from None
        if quantity < 1:
            raise ApiError(400, "quantity must be at least 1")
        customer = connection.execute("SELECT * FROM customers WHERE id = ?", (customer_id,)).fetchone()
        product = connection.execute("SELECT * FROM products WHERE id = ? AND active = 1", (product_id,)).fetchone()
        plan = connection.execute("SELECT * FROM plans WHERE id = ? AND active = 1", (plan_id,)).fetchone()
        if not customer or not product or not plan:
            raise ApiError(404, "Customer, active product, or active plan was not found")
        if quantity < plan["minimum_quantity"]:
            raise ApiError(400, f"This plan requires at least {plan['minimum_quantity']} units")
        today = date.today()
        if plan["starts_on"] and date.fromisoformat(plan["starts_on"]) > today:
            raise ApiError(400, "This plan is not available yet")
        if plan["ends_on"] and date.fromisoformat(plan["ends_on"]) < today:
            raise ApiError(400, "This plan is no longer available")
        variant_id = data.get("variantId")
        variant = None
        if variant_id is not None:
            variant = connection.execute("SELECT * FROM product_variants WHERE id = ? AND product_id = ?", (int(variant_id), product_id)).fetchone()
            if not variant:
                raise ApiError(404, "Variant was not found for this product")
        unit_price = round(product["sales_price"] + (variant["price_extra"] if variant else 0), 2)
        discount = self.number(data, "discountPercent", minimum=0, maximum=100, default=0)
        start = date.fromisoformat(data.get("startDate", date_string()))
        number = self.next_number(connection, "subscriptions", "number", "SUB-")
        next_bill = add_period(start, plan["billing_interval"], plan["interval_count"])
        end_date = data.get("endDate")
        cursor = connection.execute(
            """INSERT INTO subscriptions(number, customer_id, product_id, variant_id, plan_id,
               status, quantity, unit_price, discount_percent, start_date, next_billing_date,
               end_date, auto_renew, created_at)
               VALUES (?, ?, ?, ?, ?, 'ACTIVE', ?, ?, ?, ?, ?, ?, ?, ?)""",
            (number, customer_id, product_id, variant["id"] if variant else None, plan_id,
             quantity, unit_price, discount, date_string(start), date_string(next_bill), end_date,
             int(bool(data.get("autoRenew", True))), date_string()),
        )
        connection.commit()
        row = connection.execute("SELECT * FROM subscriptions WHERE id = ?", (cursor.lastrowid,)).fetchone()
        self.send_json(201, subscription_record(connection, row))

    def subscription_action(self, connection: sqlite3.Connection, number: str, action: str) -> None:
        row = connection.execute("SELECT * FROM subscriptions WHERE number = ?", (number,)).fetchone()
        if not row:
            raise ApiError(404, "Subscription not found")
        plan = connection.execute("SELECT * FROM plans WHERE id = ?", (row["plan_id"],)).fetchone()
        today = date.today()
        if action == "pause":
            if not plan["allow_pause"]:
                raise ApiError(400, "Pausing is disabled for this plan")
            if row["status"] != "ACTIVE":
                raise ApiError(409, "Only active subscriptions can be paused")
            connection.execute("UPDATE subscriptions SET status = 'PAUSED' WHERE id = ?", (row["id"],))
        elif action == "resume":
            if row["status"] != "PAUSED":
                raise ApiError(409, "Only paused subscriptions can be resumed")
            next_bill = row["next_billing_date"]
            if next_bill < date_string(today):
                next_bill = date_string(today)
            connection.execute("UPDATE subscriptions SET status = 'ACTIVE', next_billing_date = ? WHERE id = ?", (next_bill, row["id"]))
        elif action == "cancel":
            if not plan["allow_cancellation"]:
                raise ApiError(400, "Cancellation is disabled for this plan")
            if row["status"] == "CLOSED":
                raise ApiError(409, "Subscription is already closed")
            connection.execute("UPDATE subscriptions SET status = 'CLOSED', end_date = ?, auto_renew = 0 WHERE id = ?", (date_string(today), row["id"]))
        elif action == "renew":
            if not plan["allow_renewal"]:
                raise ApiError(400, "Renewal is disabled for this plan")
            if row["status"] not in ("ACTIVE", "CLOSED"):
                raise ApiError(409, "Only active or closed subscriptions can be renewed")
            base = date.fromisoformat(row["end_date"]) if row["end_date"] and date.fromisoformat(row["end_date"]) >= today else today
            new_end = add_period(base, plan["billing_interval"], plan["interval_count"])
            next_bill = row["next_billing_date"] if row["next_billing_date"] >= date_string(today) else date_string(today)
            connection.execute("UPDATE subscriptions SET status = 'ACTIVE', end_date = ?, next_billing_date = ?, auto_renew = 1 WHERE id = ?", (date_string(new_end), next_bill, row["id"]))
        connection.commit()
        updated = connection.execute("SELECT * FROM subscriptions WHERE id = ?", (row["id"],)).fetchone()
        self.send_json(200, subscription_record(connection, updated))

    def confirm_invoice(self, connection: sqlite3.Connection, number: str) -> None:
        row = connection.execute("SELECT * FROM invoices WHERE number = ?", (number,)).fetchone()
        if not row:
            raise ApiError(404, "Invoice not found")
        if row["status"] != "DRAFT":
            raise ApiError(409, "Only draft invoices can be confirmed")
        connection.execute("UPDATE invoices SET status = 'CONFIRMED' WHERE id = ?", (row["id"],))
        connection.commit()
        updated = connection.execute("SELECT * FROM invoices WHERE id = ?", (row["id"],)).fetchone()
        self.send_json(200, invoice_record(connection, updated))

    def run_billing(self, connection: sqlite3.Connection, data: dict) -> None:
        run_date = date.fromisoformat(data.get("runDate", date_string()))
        rows = connection.execute(
            "SELECT * FROM subscriptions WHERE status = 'ACTIVE' AND next_billing_date <= ? ORDER BY id",
            (date_string(run_date),),
        ).fetchall()
        created = []
        for sub in rows:
            plan = connection.execute("SELECT * FROM plans WHERE id = ?", (sub["plan_id"],)).fetchone()
            period_start = sub["next_billing_date"]
            subtotal = round(sub["unit_price"] * sub["quantity"], 2)
            discount = round(subtotal * sub["discount_percent"] / 100, 2)
            tax = round((subtotal - discount) * plan["tax_rate"] / 100, 2)
            total = round(subtotal - discount + tax, 2)
            number = self.next_number(connection, "invoices", "number", "INV-")
            cursor = connection.execute(
                """INSERT OR IGNORE INTO invoices(number, subscription_id, billing_period_start,
                   issue_date, due_date, status, subtotal, discount_amount, tax_rate, tax_amount,
                   total, amount_paid) VALUES (?, ?, ?, ?, ?, 'CONFIRMED', ?, ?, ?, ?, ?, 0)""",
                (number, sub["id"], period_start, date_string(run_date), date_string(run_date + timedelta(days=7)), subtotal, discount, plan["tax_rate"], tax, total),
            )
            if cursor.rowcount:
                created.append(invoice_record(connection, connection.execute("SELECT * FROM invoices WHERE id = ?", (cursor.lastrowid,)).fetchone()))
                next_date = add_period(date.fromisoformat(period_start), plan["billing_interval"], plan["interval_count"])
                connection.execute("UPDATE subscriptions SET next_billing_date = ? WHERE id = ?", (date_string(next_date), sub["id"]))
        connection.commit()
        self.send_json(200, {"createdCount": len(created), "invoices": created, "runDate": date_string(run_date)})

    def create_payment(self, connection: sqlite3.Connection, data: dict) -> None:
        invoice_number = self.required_text(data, "invoiceNumber")
        invoice = connection.execute("SELECT * FROM invoices WHERE number = ?", (invoice_number,)).fetchone()
        if not invoice:
            raise ApiError(404, "Invoice not found")
        if invoice["status"] not in ("CONFIRMED", "OVERDUE"):
            raise ApiError(409, "Payments can only be recorded for confirmed invoices")
        amount = self.number(data, "amount", minimum=0.01)
        balance = round(invoice["total"] - invoice["amount_paid"], 2)
        if amount > balance:
            raise ApiError(400, f"Payment exceeds the remaining balance of {balance:.2f}")
        method = str(data.get("method", "Manual")).strip() or "Manual"
        paid_at = str(data.get("paidAt", date_string()))
        cursor = connection.execute(
            "INSERT INTO payments(invoice_id, amount, method, paid_at, note) VALUES (?, ?, ?, ?, ?)",
            (invoice["id"], amount, method, paid_at, str(data.get("note", ""))),
        )
        new_paid = round(invoice["amount_paid"] + amount, 2)
        new_status = "PAID" if new_paid >= invoice["total"] else "CONFIRMED"
        connection.execute("UPDATE invoices SET amount_paid = ?, status = ? WHERE id = ?", (new_paid, new_status, invoice["id"]))
        connection.commit()
        payment = connection.execute("SELECT * FROM payments WHERE id = ?", (cursor.lastrowid,)).fetchone()
        updated_invoice = connection.execute("SELECT * FROM invoices WHERE id = ?", (invoice["id"],)).fetchone()
        result = {
            "id": payment["id"], "invoiceId": payment["invoice_id"], "invoiceNumber": invoice_number,
            "amount": round(payment["amount"], 2), "method": payment["method"], "paidAt": payment["paid_at"],
            "note": payment["note"], "currency": CURRENCY,
            "invoice": invoice_record(connection, updated_invoice),
        }
        self.send_json(201, result)

    def required_text(self, data: dict, key: str) -> str:
        value = str(data.get(key, "")).strip()
        if not value:
            raise ApiError(400, f"{key} is required")
        return value

    def number(self, data: dict, key: str, minimum: float, maximum: float | None = None, default: float | None = None) -> float:
        try:
            value = float(data.get(key, default))
        except (ValueError, TypeError):
            raise ApiError(400, f"{key} must be a number") from None
        if value < minimum or (maximum is not None and value > maximum):
            suffix = f" and at most {maximum}" if maximum is not None else ""
            raise ApiError(400, f"{key} must be at least {minimum}{suffix}")
        return value

    def next_number(self, connection: sqlite3.Connection, table: str, column: str, prefix: str) -> str:
        rows = connection.execute(f"SELECT {column} FROM {table} WHERE {column} LIKE ?", (prefix + "%",)).fetchall()
        maximum = 0
        for row in rows:
            digits = re.search(r"(\d+)$", row[column])
            if digits:
                maximum = max(maximum, int(digits.group(1)))
        return f"{prefix}{maximum + 1:04d}"


def main() -> None:
    initialize()
    print(f"Brightloop Subscription API running at http://{HOST}:{PORT}")
    print(f"Using local demo database: {DB_PATH}")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
