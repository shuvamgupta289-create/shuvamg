# STEPZONE

STEPZONE is a Flask 3 sneaker shop with a Jinja storefront, SQLAlchemy models, PostgreSQL support, local SQLite development, customer accounts, shopping cart and wishlist, COD and Paytm checkout, and an administrator dashboard.

## Features

- Brand and category browsing, product search, filters, sorting, and pagination.
- Customer registration, sign-in, profile, wishlist, cart, and order history.
- Cash on Delivery and Paytm checkout, with stock reservation for pending Paytm payments.
- Admin product, brand, inventory, order, and customer management.
- Order confirmation emails through Brevo.
- Vercel Python entry point at `api/index.py`.

## Requirements and local setup

- Python 3.12 (see `.python-version`).
- PowerShell on Windows or a POSIX shell.

```powershell
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

The development default is a project-local SQLite database when `DATABASE_URL` is unset. Keep development and test configuration pointed at local SQLite. The pytest configuration forcibly sets an in-memory SQLite URL before importing the app and disables dotenv loading, so tests do not use a developer's database URL or `.env`.

Start locally:

```powershell
$env:APP_ENV = "development"
$env:FLASK_APP = "wsgi.py"
flask run
```

## Environment variable names

Configure these in the environment that runs the application. Never commit real values.

- Core: `APP_ENV`, `FLASK_ENV`, `SECRET_KEY`, `DATABASE_URL`, `PUBLIC_BASE_URL`.
- Paytm: `PAYTM_MID`, `PAYTM_MERCHANT_KEY`, `PAYTM_WEBSITE`, `PAYTM_ENVIRONMENT`, `PAYTM_CALLBACK_URL`.
- Brevo: `BREVO_API_KEY`, `BREVO_SENDER_EMAIL`, `BREVO_SENDER_NAME`.
- Rate limiting: `RATELIMIT_ENABLED`, `RATELIMIT_STORAGE_URI`, `CUSTOMER_LOGIN_RATE_LIMIT`, `ADMIN_LOGIN_RATE_LIMIT`, `REGISTRATION_RATE_LIMIT`, `FORGOT_PASSWORD_RATE_LIMIT`.
- Runtime/platform: `VERCEL`, `FLASK_APP`, `PYTHON_DOTENV_DISABLED`.

`PAYTM_ENVIRONMENT` selects `staging` or `production` gateway URLs. When production Paytm is selected in the production app configuration, startup requires the Paytm merchant ID, merchant key, website name, and callback URL. Rate limiting uses an in-memory store by default; use a shared production store when running multiple instances.

## Database migrations

The checked-in Alembic history includes the order inventory-reservation flags and the non-negative stock constraint. Before any migration, verify the active `DATABASE_URL` points to the intended database and review a backup and migration plan. This project documentation does not authorize production database changes.

```powershell
flask db heads
flask db upgrade
```

Do not run the upgrade command against production without a separate reviewed approval.

## Tests and coverage

```powershell
python -m pytest -q
python -m pytest -q --cov=app.routes.checkout --cov=app.services --cov-report=term-missing --cov-fail-under=85
```

Paytm and Brevo integrations are mocked in tests; the suite makes no payment or email requests.

## Useful maintenance commands

```powershell
flask expire-pending-orders --minutes 30
flask retry-failed-emails --limit 100
```

The first command marks stale pending Paytm orders expired and releases their reservations. The second retries a bounded batch of failed order-confirmation emails. Refund processing is not automatic: paid cancellations are marked `refund_pending` for an administrator to review through the existing external payment process.

## Vercel deployment

Vercel uses `api/index.py` and `vercel.json`; `.python-version` pins the runtime. Configure the required environment-variable names above in Vercel, including a PostgreSQL `DATABASE_URL` and `SECRET_KEY`. Production rejects SQLite. Review `requirements.txt` and the migration heads before deployment. Apply schema changes only through a separately approved database operation, then deploy the reviewed Git revision through the normal release process.

`local_test_data/`, the local preview launcher, tests, and SQLite files are excluded from Vercel packaging by `.vercelignore`.
