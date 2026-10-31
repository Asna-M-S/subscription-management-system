# Subscription Management System

A hackathon project for managing Brightloop Software's subscription lifecycle: products and plans, quotations, subscriptions, recurring invoices, discounts, payments, and revenue reporting.

## Project status

The Odoo workspace has a demo product, monthly plan, active subscription, quotation template, and draft invoice. This repository now also contains a small local REST API backed by SQLite so the frontend and dashboard teammates can work against real endpoints.

The local API database is separate from the hosted Odoo database. Odoo records do not sync to it yet; the API starts with its own clearly named demo records.

## Team responsibilities

- **Odoo business logic:** products, variants, subscription plans, quotations, subscription states, invoices, taxes, discounts, and payments.
- **Customer interface:** account access and subscription/invoice screens.
- **Automation:** scheduled billing triggers, reminders, renewal notices, and payment updates.
- **Dashboard and integration:** subscription, revenue, payment, and overdue-invoice summaries.

## Core demonstration flow

1. Create a product and a monthly subscription plan.
2. Create a customer quotation and confirm it as a subscription.
3. Generate the invoice for the due billing period.
4. Record a payment against the invoice.
5. Show the updated subscription, invoice, and payment in the customer interface and financial dashboard.

## Sample data for the demo

- Product: `Brightloop Inventory`
- Base price: INR 1,000 per seat per month
- Variant: `Odoo`, adding INR 560 per seat
- Customer: `Sunmart`
- Quantity: 10 seats
- Example discount: 10% for 10 or more seats

Use only test data during the hackathon. Tax rates should follow the value selected for the demo; the problem statement does not prescribe a rate.

## Integration

The API fields and routes are documented in [`docs/dashboard-api.md`](docs/dashboard-api.md). The Odoo connection is still pending. Do not commit passwords, API keys, or `.env` files.

## Run the local API

Requires Python 3.10 or newer; no packages need to be installed.

```bash
python3 backend/server.py
```

The server starts at `http://127.0.0.1:8000`. Visit `/health` to see its status. SQLite data is saved to `data/subscriptions.sqlite3` and is ignored by Git. To reset the local demo database, stop the server, remove that file, and start the server again; it will recreate the seed records.

The API currently supports customers, products and variants, recurring plans, subscriptions and lifecycle actions, invoice generation/confirmation, partial and full payment recording, and dashboard summaries. Authentication, production deployment, and live Odoo synchronization still need to be added before real customer or financial data is used.
