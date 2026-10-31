# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some Oxlint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the Oxlint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and Oxlint's TypeScript related rules in your project.

## BrightLoop dashboard API

The dashboard uses local sample data until `VITE_DASHBOARD_API_URL` is configured. Set it to the full Django REST endpoint URL (for example, in a local `.env` file) to load live data. Do not put secret keys in `VITE_` variables; Vite exposes them to browser code.

The endpoint should return JSON with this shape:

```json
{
  "summary": {
    "activeSubscriptions": 1248,
    "monthlyRecurringRevenue": 1842500,
    "revenueCollectedThisMonth": 1624800,
    "outstandingAmount": 217700,
    "pendingAmount": 8400,
    "overdueAmount": 68400,
    "overdueInvoicesCount": 8
  },
  "transactions": [],
  "overdueInvoices": [],
  "calendarPayments": {},
  "revenueSeries": {
    "Weekly": [],
    "Monthly": [],
    "Yearly": []
  },
  "collectionSuccessRate": 94.8
}
```

Each transaction needs `name`, `id`, `date`, `method`, `status`, and numeric `amount`. Overdue invoice records need `id`, `customer`, `dueDate`, `amount`, and `daysOverdue`. Calendar payment entries use `customer`, `method`, `status`, and numeric `amount`, grouped under ISO date keys such as `2026-10-31`. Revenue series points use a string `label` and numeric `revenue`. Invalid API responses and request errors are shown in the dashboard while sample data remains visible.
