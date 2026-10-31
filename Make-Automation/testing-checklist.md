# Testing Checklist

## Connection
- [ ] Confirm Odoo Online plan and version with the database owner.
- [ ] Confirm external API access is available.
- [ ] Create a dedicated integration user with only the required permissions.
- [ ] Store credentials securely; never commit them to GitHub.
- [ ] Test Make's connection to the correct team database.

## Recurring invoice
- [ ] Create or identify one sample active subscription due for billing.
- [ ] Run the scenario once.
- [ ] Verify that the expected invoice appears in Odoo.
- [ ] Verify customer, invoice lines, quantities, prices, and taxes.
- [ ] Run the scenario again for the same billing period.
- [ ] Verify that a duplicate invoice is not created.

## Exceptions
- [ ] Test a subscription that is not active.
- [ ] Test a subscription whose billing date is in the future.
- [ ] Test an existing invoice for the same billing period.
- [ ] Test an API or permission failure.
- [ ] Verify failed processing is not marked as successful.

## Reminders
- [ ] Test a subscription approaching renewal.
- [ ] Test an overdue unpaid invoice.
- [ ] Verify the intended recipient and message content.

## Evidence for demonstration
- [ ] Screenshot of the Make scenario.
- [ ] Screenshot of the generated sample invoice in Odoo.
- [ ] Screenshot or run history showing the duplicate was skipped.
- [ ] Screenshot of a reminder test, if implemented.
