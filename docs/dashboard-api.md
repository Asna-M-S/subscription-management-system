# Odoo-backed REST API

**Source of truth:** the hosted Odoo 20 database at `brightloop-software.odoo.com`. This backend does not use SQLite or seed business records. It forwards requests to Odoo's JSON-2 external API and shapes the response for the team UI.

## Connection setup

Odoo external API access is available only on a **Custom** plan. The account owner must create an API key from the Odoo user's **Preferences → Account Security → New API Key** page and keep it private. Copy `.env.example` to `.env`, then set `ODOO_API_KEY` in that local file. The Odoo API key must never go in frontend code, a public repository, or a chat. The API key user also needs the Odoo access groups for each model and action used.

Start the bridge from the repository root with `python3 backend/server.py`. It listens on `http://127.0.0.1:8000`. `GET /health` checks the local server; `GET /api/v1/health/odoo` makes an authenticated read from Odoo. If the key is missing or rejected, the business routes return an error instead of sample records.

If `APP_API_TOKEN` is set in `.env`, send it to this bridge as `Authorization: Bearer <app-token>`. This is a separate token for the team's backend; never share the Odoo key with a browser app. If the bridge runs on a server or listens beyond localhost, set `APP_API_TOKEN` and use HTTPS.

All business endpoints use the Odoo user's permissions. Dates use `YYYY-MM-DD`, the default display currency is `INR`, and list endpoints use `{ "items": [], "pagination": { "page": 1, "limit": 20, "total": 0 } }`.

## Routes

| Method | Route | Odoo operation |
|---|---|---|
| GET | `/api/v1/health/odoo` | Read company to verify authenticated access |
| GET | `/api/v1/dashboard/summary` | Aggregate live subscriptions, invoices, and payments |
| GET, POST | `/api/v1/customers` | Read or create `res.partner` |
| GET, POST | `/api/v1/products` | Read or create `product.template` |
| GET, POST | `/api/v1/plans` | Read or create `sale.subscription.plan` |
| GET, POST | `/api/v1/subscriptions` | Read, or create and confirm a subscription order |
| GET | `/api/v1/subscriptions/{number}` | Read a subscription such as `S00001` |
| GET | `/api/v1/billing/due?asOf=YYYY-MM-DD` | List live subscriptions whose next invoice date is due |
| POST | `/api/v1/subscriptions/{number}/pause` | Call Odoo `pause_subscription` |
| POST | `/api/v1/subscriptions/{number}/resume` | Call Odoo `resume_subscription` |
| POST | `/api/v1/subscriptions/{number}/cancel` | Call Odoo `set_close` |
| GET | `/api/v1/invoices` | Read `account.move` customer invoices |
| POST | `/api/v1/invoices/{number}/post` | Post a draft invoice in Odoo (`/confirm` is an alias) |
| GET | `/api/v1/payments` | Read inbound Odoo payments |
| GET | `/api/v1/payment-options` | Return available journals and inbound payment methods |
| POST | `/api/v1/payments` | Register a payment using Odoo's accounting payment wizard |

List routes accept `page` and `limit` query parameters. Subscriptions and invoices also accept `status`. Payments accept `from` and `to` dates.

## Dashboard summary fields

`GET /api/v1/dashboard/summary`

```json
{
  "currency": "INR",
  "activeSubscriptions": 1,
  "monthlyRecurringRevenue": 9000.0,
  "revenueCollectedThisMonth": 0.0,
  "outstandingAmount": 10620.0,
  "overdueAmount": 0.0,
  "overdueInvoicesCount": 0
}
```

Values above illustrate the response shape only; live totals come from Odoo. `monthlyRecurringRevenue` sums Odoo's monthly-equivalent recurring value for active subscriptions before tax. It excludes paused and closed subscriptions. Outstanding and overdue amounts use the residual balance on posted customer invoices. Collected revenue counts inbound payments Odoo marks paid or in process during the current month.

## Subscription response fields

`GET /api/v1/subscriptions?status=ACTIVE`

Fields: `id`, `number`, `customerName`, `productName`, `variantName`, `planName`, `status`, `billingInterval`, `startDate`, `nextBillingDate`, `endDate`, `quantity`, `unitPrice`, `discountPercent`, `recurringAmount`, `monthlyRecurringRevenue`, `currency`, and `autoRenew`.

The bridge maps Odoo subscription states to `QUOTATION`, `ACTIVE`, `PAUSED`, `CLOSED`, and `CONFIRMED`. Some plan features such as minimum quantity or availability dates are included only if this Odoo database exposes those fields; Odoo's standard plan model may not have them.

Product responses include Odoo variant IDs and variant details (name, SKU, prices, and attribute values) so the UI can show configured variants.

Create request example:

```json
{
  "customerId": 42,
  "productId": 17,
  "planId": 3,
  "quantity": 10,
  "discountPercent": 10,
  "startDate": "2026-10-31"
}
```

This creates a real Odoo subscription sale order and confirms it. IDs are Odoo record IDs returned by the corresponding list endpoints.

## Invoice and payment response fields

Invoice fields: `id`, `number`, `customerName`, `subscriptionId` (Odoo invoice origin), `issueDate`, `dueDate`, `status`, `subtotal`, `discountAmount`, `taxAmount`, `total`, `amountPaid`, `balanceDue`, and `currency`.

Payment fields: `id`, `invoiceId`, `invoiceNumber`, `customerName`, `amount`, `method`, `paidAt`, `note`, `currency`, and `status`.

Payment registration request example:

```json
{
  "invoiceNumber": "INV/26-27/0001",
  "amount": 10620,
  "journalId": 1,
  "paymentMethodLineId": 1,
  "paidAt": "2026-10-31",
  "note": "Hackathon test payment"
}
```

Use the actual IDs from `/api/v1/payment-options`. The endpoint rejects a draft invoice and an amount larger than the current balance. Submitting it creates a real accounting payment in Odoo, so use it only for an intended test payment.

## Recurring invoices

Recurring invoices must be generated by Odoo's subscription billing process/scheduled action. This bridge reads those invoices after Odoo creates them; it does not create a fake invoice in a separate database or trigger an unverified billing method. To demonstrate one now, use the subscription's invoice action in Odoo, then the generated invoice appears at `GET /api/v1/invoices`.

The automation teammate can call `/api/v1/billing/due` to see which real subscriptions are due, then rely on Odoo's scheduled billing action to create the accounting invoices.

## Current Odoo record references

The Odoo database previously showed subscription `S00001` and draft invoice `INV/26-27/0001`. The draft invoice total was reviewed as ₹10,620 (₹9,000 subtotal plus ₹1,620 tax), with no payment recorded then. Verify the current live record state in Odoo before using it in a presentation.
