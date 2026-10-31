# Brightloop Subscription Management System

Hackathon backend for Brightloop Software's subscription lifecycle. The hosted Odoo database is the source of truth for customers, products, subscription plans, subscriptions, invoices, and payments. The Python server in this repository is a small REST bridge to Odoo; it does not seed or store a second set of business records.

## Odoo connection requirement

The team's database is Odoo 20 Enterprise. Odoo's external JSON-2 API requires a **Custom** subscription plan. Standard and One App Free plans do not include external API access. If this database is on a trial or another plan, check the Odoo subscription page before expecting the REST bridge to connect.

Create an API key while signed in to the Odoo user that should access the records: open your avatar menu → **My Profile / Preferences** → **Account Security** → **New API Key**. Give it a short expiry, copy it once, and save it only in the local `.env` file. The key is shown only once. Do not put it in GitHub, frontend code, or a chat message. The API user needs read access to customers, products, subscriptions, invoices, and payments; write access is needed for create and lifecycle routes.

## Start the Odoo-backed API

1. Copy `.env.example` to `.env` in the repository root.
2. Keep the Odoo URL and database name shown in `.env.example` and enter the API key locally as `ODOO_API_KEY=...`.
3. From the repository root, run:

   ```bash
   python3 backend/server.py
   ```

4. Open `http://127.0.0.1:8000/health` for local server status, then `http://127.0.0.1:8000/api/v1/health/odoo` to verify an authenticated read from Odoo.

The server uses only Python's standard library. If a teammate's browser app calls it, keep the Odoo key on this backend. Share an `APP_API_TOKEN` with the teammate through a private channel if you set one. Do not place the Odoo key in browser JavaScript. For a server on another computer, deploy it over HTTPS and set a strong `APP_API_TOKEN`; do not expose the local server publicly without authentication.

## API contract

Routes and JSON response shapes are in [`docs/dashboard-api.md`](docs/dashboard-api.md). The REST bridge reads live Odoo records and performs supported actions through Odoo's JSON-2 model API. Recurring invoice creation remains Odoo's own subscription billing process; the bridge shows invoices created there. Payment registration uses Odoo's accounting payment wizard and creates a real Odoo payment record.

## Demo reference records

The hosted database previously contained subscription `S00001` and draft invoice `INV/26-27/0001` for review. The invoice was described as ₹10,620 total (₹9,000 subtotal + ₹1,620 GST), with no payment recorded. These are Odoo records, not seeded API fixtures. Confirm their current state in Odoo before presenting them.

## Local-only demo

`backend/local_demo_server.py` is the earlier SQLite sample server. It is retained only for reference and is not the backend to use for the actual Odoo-connected application.
