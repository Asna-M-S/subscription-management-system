# Financial dashboard API contract

**Status:** Implemented by the local Python/SQLite API in `backend/server.py`. Hosted Odoo synchronization is not connected yet.

## Start the local API

From the repository root, run `python3 backend/server.py`. It listens at `http://127.0.0.1:8000` and creates `data/subscriptions.sqlite3` with local demo records on first start. No external packages are required.

The local demo database is separate from Odoo. Its sample subscription is `SUB-0001` and its sample invoice is `INV-0001`; these are not the Odoo records listed below.

## Implemented routes

| Method | Route | Purpose |
|---|---|---|
| GET | `/api/v1/dashboard/summary` | Revenue, active subscriptions, and outstanding invoices |
| GET, POST | `/api/v1/customers` | List or create customers |
| GET, POST | `/api/v1/products` | List or create products and variants |
| GET, POST | `/api/v1/plans` | List or create recurring plans |
| GET, POST | `/api/v1/subscriptions` | List or create subscriptions |
| GET | `/api/v1/subscriptions/{number}` | Subscription detail |
| POST | `/api/v1/subscriptions/{number}/pause` | Pause an active subscription |
| POST | `/api/v1/subscriptions/{number}/resume` | Resume a paused subscription |
| POST | `/api/v1/subscriptions/{number}/renew` | Renew an active or closed subscription |
| POST | `/api/v1/subscriptions/{number}/cancel` | Close a subscription |
| GET | `/api/v1/invoices` | List/filter invoices |
| POST | `/api/v1/invoices/{number}/confirm` | Confirm a draft invoice |
| POST | `/api/v1/billing/run` | Generate invoices for active subscriptions due on or before `runDate` |
| GET, POST | `/api/v1/payments` | List payments or record a partial/full demo payment |

For local frontend development, the API allows cross-origin requests. It has no authentication or payment gateway yet and is intended for hackathon demo data only.

## Odoo demo records

Use these records as reference data while building the dashboard with mock data. They are stored in the Odoo database and are not returned by the API yet.

| Record | Details |
|---|---|
| Customer | Sunmart Hackathon Demo |
| Subscription | `S00001` — Brightloop Monthly, In Progress, 10 units, 10% discount |
| Subscription value | ₹9,000 monthly recurring revenue before tax |
| Invoice | `INV/26-27/0001` — draft, linked to `S00001` |
| Invoice totals | ₹9,000 subtotal + ₹1,620 GST = ₹10,620 total |
| Invoice balance display | ₹10,620 Amount Due after refreshing the GST tax selection |

These are demo records. The invoice remains a draft and no payment has been recorded. Do not treat them as live API responses or payment data.

## Conventions

- Prefix: `/api/v1`
- Dates: `YYYY-MM-DD`
- Currency: `INR`
- Amounts: JSON numbers in rupees, with two decimal places where needed.
- List response: `{ "items": [], "pagination": { "page": 1, "limit": 20, "total": 0 } }`

## Dashboard summary

`GET /api/v1/dashboard/summary`

```json
{
  "currency": "INR",
  "activeSubscriptions": 1,
  "monthlyRecurringRevenue": 9000.00,
  "revenueCollectedThisMonth": 0.00,
  "outstandingAmount": 10620.00,
  "overdueAmount": 0.00,
  "overdueInvoicesCount": 0
}
```

`monthlyRecurringRevenue` is the monthly-equivalent value of active subscriptions, after recurring discounts and before tax. Paused and closed subscriptions, taxes, and one-time charges are excluded.

## Subscriptions

`GET /api/v1/subscriptions?status=ACTIVE&page=1&limit=20`

Each item contains: `id`, `number`, `customerName`, `productName`, `variantName`, `planName`, `status`, `billingInterval`, `startDate`, `nextBillingDate`, `endDate`, `quantity`, `unitPrice`, `discountPercent`, `recurringAmount`, `monthlyRecurringRevenue`, `currency`, and `autoRenew`.

Statuses: `DRAFT`, `QUOTATION`, `CONFIRMED`, `ACTIVE`, `PAUSED`, `CLOSED`.

Create subscriptions with `customerId`, `productId`, `planId`, `quantity`, and optional `variantId`, `discountPercent`, `startDate`, `endDate`, and `autoRenew`. IDs for the seeded customer, product, variant, and plan are available from their respective list endpoints.

## Invoices

`GET /api/v1/invoices?status=OVERDUE&page=1&limit=20`

Each item contains: `id`, `number`, `customerName`, `subscriptionId`, `issueDate`, `dueDate`, `status`, `subtotal`, `discountAmount`, `taxAmount`, `total`, `amountPaid`, `balanceDue`, and `currency`.

Statuses: `DRAFT`, `CONFIRMED`, `PAID`, `OVERDUE`, `CANCELLED`.

## Payments

`GET /api/v1/payments?from=2026-10-01&to=2026-10-31&page=1&limit=20`

Each item contains: `id`, `invoiceId`, `invoiceNumber`, `customerName`, `amount`, `method`, `paidAt`, `note`, and `currency`.

To record a payment, send `POST /api/v1/payments` with `invoiceNumber`, `amount`, and optional `method`, `paidAt`, and `note`. The API rejects payments larger than the remaining balance. A payment is a local demo record only; it does not charge a card or move money.
