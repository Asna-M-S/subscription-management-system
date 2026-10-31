# Dashboard Test Checklist

## Summary cards
- [ ] Active subscriptions count is displayed.
- [ ] Monthly recurring revenue is displayed in INR.
- [ ] Revenue collected this month is displayed.
- [ ] Outstanding amount is displayed.
- [ ] Overdue amount and overdue invoice count are displayed.
- [ ] Empty or unavailable data is handled clearly.

## Active subscriptions
- [ ] Subscription number, customer, plan, status, and billing interval are shown.
- [ ] Start date and next billing date are shown.
- [ ] Quantity and recurring amount are shown.
- [ ] Status filter and pagination work.

## Overdue invoices
- [ ] Invoice number, customer, issue date, and due date are shown.
- [ ] Total, amount paid, and balance due are shown.
- [ ] Overdue status is clear.
- [ ] Status filter and pagination work.

## Payments
- [ ] Invoice number, customer, amount, method, and payment date are shown.
- [ ] Date-range filter works.
- [ ] Pagination works.

## General
- [ ] Dashboard handles loading and API errors.
- [ ] INR values and dates are formatted consistently.
- [ ] Dashboard remains readable on smaller screens.
- [ ] Totals match the displayed records and API response.