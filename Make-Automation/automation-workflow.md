# Automation Workflow

## Objective
Automate recurring invoice generation for active subscriptions while reducing missed or duplicate invoices.

## Proposed flow
Scheduler → Find due active subscriptions → Check invoice for subscription + billing period → Create invoice if missing → Record successful processing.

## Required subscription information
The workflow is expected to use the subscription's identifier, customer, status, billing interval, next billing date, products or plan lines, quantities, prices, and applicable taxes. The exact Odoo fields must be confirmed against the team's database and version.

## Duplicate prevention
Use a stable key made from the subscription identifier and billing period, for example:

`SUB001-2026-10`

Before creating an invoice, search for an existing invoice or processing record with the same subscription and billing period. Create only when no match exists.

## Failure handling
- If Odoo cannot be reached, stop and record the error.
- If invoice creation fails, do not mark the period as successfully billed.
- If the invoice already exists, skip creation and record that it was skipped as a duplicate.
- Test with sample records before using real customer data.

## Status
Design only. The live Make scenario and Odoo API calls have not yet been configured or tested.
