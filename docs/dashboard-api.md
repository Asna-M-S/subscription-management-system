# Financial dashboard API contract

**Status:** Proposed contract for the dashboard mock data. Endpoints are not live until the backend/Odoo integration is connected.

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
  "activeSubscriptions": 24,
  "monthlyRecurringRevenue": 38400.00,
  "revenueCollectedThisMonth": 76800.00,
  "outstandingAmount": 12000.00,
  "overdueAmount": 3000.00,
  "overdueInvoicesCount": 2
}
```

`monthlyRecurringRevenue` is the monthly-equivalent value of active subscriptions, after recurring discounts and before tax. Paused and closed subscriptions, taxes, and one-time charges are excluded.

## Subscriptions

`GET /api/v1/subscriptions?status=ACTIVE&page=1&limit=20`

Each item contains: `id`, `number`, `customerName`, `planName`, `status`, `billingInterval`, `startDate`, `nextBillingDate`, `quantity`, `recurringAmount`, and `currency`.

Statuses: `DRAFT`, `QUOTATION`, `CONFIRMED`, `ACTIVE`, `PAUSED`, `CLOSED`.

## Invoices

`GET /api/v1/invoices?status=OVERDUE&page=1&limit=20`

Each item contains: `id`, `number`, `customerName`, `subscriptionId`, `issueDate`, `dueDate`, `status`, `subtotal`, `discountAmount`, `taxAmount`, `total`, `amountPaid`, `balanceDue`, and `currency`.

Statuses: `DRAFT`, `CONFIRMED`, `PAID`, `OVERDUE`, `CANCELLED`.

## Payments

`GET /api/v1/payments?from=2026-10-01&to=2026-10-31&page=1&limit=20`

Each item contains: `id`, `invoiceId`, `invoiceNumber`, `customerName`, `amount`, `method`, `paidAt`, `note`, and `currency`.
