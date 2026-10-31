# Billing Logic

## Recurring billing
A subscription should be considered for billing when:
- its status is active; and
- its next billing date is due according to the agreed schedule.

## Invoice creation
For each due subscription:
1. Determine the billing period.
2. Build a unique subscription-period key.
3. Search for an invoice or processing record for that key.
4. If found, skip invoice creation.
5. If not found, create the invoice in Odoo using the subscription's customer, lines, quantities, prices, and taxes.
6. Confirm that Odoo returned a successful invoice record.
7. Only then record the period as processed and update the next billing date, if that update is part of the agreed design.

## Reminders
Planned reminder workflows:
- Renewal notification before a subscription's renewal date.
- Overdue payment reminder when an invoice remains unpaid after its due date.

Reminder timing, recipients, and message templates must be agreed with the team.

## Assumptions to confirm
- Odoo edition, version, and subscription plan.
- Whether external API access is enabled for the Odoo Online database.
- The exact subscription and invoice fields/models available in the team's database.
- The team's billing-day and reminder rules.
