# Admin Package Extraction Boundary

`admin/` is the single folder intended to be cut from this repository and pasted into a standalone admin-panel repository. It contains the admin dashboard, admin API, database configuration, database models, admin frontend templates/assets, admin middleware, and supporting helpers.

## Run standalone locally

From this repository you can now run only the admin panel:

```bash
cd admin
python app.py
# or: python run_local.py
```

The standalone admin app listens on port `5001` by default, serves a polished landing page at `/`, and exposes `/admin/login`, `/admin/dashboard`, `/flask-admin/`, `/admin/api/...`, `/health`, and `/health/db`.

For local development, `admin/app.py` loads `.env.local`/`.env` from the project root and from `admin/`. If `DATABASE_URL` is missing in development, it uses `admin/instance/admin.db` so the admin app can boot without the website application.

## Module layout

- `app.py` - standalone admin Flask app factory and local entrypoint.
- `run_local.py` - small local runner for the standalone admin app.
- `__init__.py` - admin blueprint plus admin template/static path constants.
- `auth.py` - Supabase/local admin authentication helpers.
- `extensions.py` - shared admin extension instances such as the rate limiter.
- `flask_admin_setup.py` - Flask-Admin dashboard, model views, imports/exports, backup screen, and POD admin actions.
- `api/` - admin-owned JSON API endpoints exposed to trusted callers, including `/admin/api/consignments/<number>` for `/track` lookups.
- `controllers/` - admin JSON response, serialization, and backup payload helpers.
- `db/` - database URL validation, engine options, request session middleware, schema maintenance, seeding, and transaction helpers.
- `frontend/` - admin login/Flask-Admin templates and admin JavaScript assets.
- `middleware/` - admin URL authentication middleware.
- `models/` - SQLAlchemy database object and admin-managed models.
- `routes/` - admin route modules.
- `services/` - admin-only service modules for import/export, POD storage, logistics validation, and PDF export.
- `static/` - admin-only static CSS served by the admin blueprint.
- `utils/` - admin-local utility helpers.

The public website should call the admin API instead of reading admin database tables directly. In this repository, `services/dashboard_api.py` is intentionally kept outside `admin/` because it is the website-side client used by `/track` to call the admin API.
