# Production preflight requirements

Run the preflight only after a verified, non-empty PostgreSQL backup is stored outside Git and its restore procedure has been checked.

The operator must provide `DATABASE_URL` through the deployment environment or a secure shell environment. The script never loads `.env` and never prints the URL.

After explicit authorization for the read-only check, run:

```powershell
$env:PYTHON_DOTENV_DISABLED = 'true'
python scripts/production_preflight.py --execute --confirm-read-only-production
```

The script begins a PostgreSQL read-only transaction, checks the applied Alembic revision, confirms that no `product_variants.stock_quantity` values are negative, and inspects the reservation columns and stock constraint. It performs no migrations or data changes.
