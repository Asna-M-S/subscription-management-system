# Brightloop Subscription Management – Make Automation

## Purpose
This folder documents the Make automation work for the Brightloop Subscription Management System.

The intended automation is to connect Make with the team's Odoo Online database and support recurring billing, renewal reminders, overdue-payment reminders, and duplicate-invoice prevention.

## Current progress
- Make account created.
- A Make scenario was created.
- The Odoo app in Make was explored.
- The available Odoo modules shown did not include invoice operations.
- The team identified the shared Odoo database as Odoo Online.
- Odoo plan and version still need confirmation.
- Make-to-Odoo API connection and all billing automations are pending.

## Planned workflow
1. Run the scenario on a schedule.
2. Find active subscriptions due for billing.
3. Check whether an invoice already exists for the subscription and billing period.
4. If no matching invoice exists, create the invoice in Odoo.
5. Record the billing period or update the relevant status.
6. Log errors and avoid marking a failed invoice as completed.

## Important
This repository contains planning and documentation only. It does not claim that the Odoo connection or automation is already working.
Do not commit API keys, passwords, database credentials, customer personal data, or exported production records.
