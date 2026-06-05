# Project guide

This project is a Flask web app for a logistics/admin portal. It has public website pages, shipment tracking, admin screens, database models, services, middleware, and tests.

## File and folder purposes

- `README.md` explains how to set up, run, and test the app locally.
- `run_local.py` starts the app for local development.
- `config.py` stores app configuration values loaded from environment variables.
- `docker-compose.yml` starts supporting local services such as PostgreSQL.
- `requirements.txt` lists Python packages needed by the app.
- `pytest.ini` stores pytest settings.
- `conftest.py` contains shared top-level test setup.
- `admin/` contains private admin screens and admin authentication helpers.
- `controllers/` contains response and data-preparation helpers.
- `db/` contains database connection, session, maintenance, and seed helpers.
- `frontend/` contains templates, JavaScript, CSS, images, fonts, and other browser assets.
- `middleware/` contains request/response protection, logging, and error handling.
- `models/` contains database table definitions.
- `routes/` connects URLs to page and form handlers.
- `scripts/` contains developer helper scripts.
- `services/` contains business logic and import/export workflows.
- `tests/` contains automated and manual checks.
- `utils/` contains shared utility helpers.
- `guide.md` is this plain-language guide to the project root.
