# Subscription Management System

A hackathon project for managing Brightloop Software's subscription lifecycle: products and plans, quotations, subscriptions, recurring invoices, discounts, payments, and revenue reporting.

## Project status

The Odoo workspace is being configured with the Sales, Subscriptions, and Invoicing apps. This repository is the team's shared project space for implementation notes and integration contracts. Odoo customer and accounting records remain in the Odoo database and are not stored in GitHub.

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

The proposed dashboard response fields are documented in [`docs/dashboard-api.md`](docs/dashboard-api.md). The team should confirm the available Odoo integration method for its database before treating the proposed endpoints as live. Do not commit passwords, API keys, or `.env` files.
