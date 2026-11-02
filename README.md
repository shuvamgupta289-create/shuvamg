# STEPZONE

STEPZONE is a sneaker e-commerce application built with Flask, SQLAlchemy, and Jinja2.

> Step Into Your Style.

## Feature 01: Project Foundation

This feature provides the Flask application factory, modular package structure, SQLAlchemy and Flask-Migrate extensions, environment-based configuration, and working home and health-check endpoints.

Supabase, PostgreSQL, authentication, catalogue features, payments, and customer-facing pages are intentionally not connected yet.

## Requirements

- Python 3.11 or newer
- PowerShell on Windows

## Setup

From the project root in PowerShell:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Set a real `SECRET_KEY` in `.env` before using the application beyond local development. The default development database is local SQLite; no Supabase connection is made in this feature.

## Run

```powershell
$env:FLASK_APP = "wsgi.py"
$env:FLASK_ENV = "development"
flask run
```

Open <http://127.0.0.1:5000/> or <http://127.0.0.1:5000/health>.

## Database migrations

The migration extension is configured, but no application models exist yet. Initialize migrations after the first model is added:

```powershell
flask db init
flask db migrate -m "Initial schema"
flask db upgrade
```
