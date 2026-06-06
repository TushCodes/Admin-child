# Admin Package Extraction Boundary

`admin/` is the single folder intended to be cut from this repository and pasted into a standalone admin-panel repository. It contains the admin dashboard, admin API, database configuration, database models, admin frontend templates/assets, admin middleware, and supporting helpers.

## Module layout

- `__init__.py` - admin blueprint, admin template/static path constants, and route-module registration.
- `auth.py` - Supabase/local admin authentication helpers.
- `flask_admin_setup.py` - Flask-Admin dashboard, model views, imports/exports, backup screen, and POD admin actions.
- `api/` - admin-owned JSON API endpoints exposed to trusted callers, including `/admin/api/consignments/<number>` for `/track` lookups.
- `controllers/` - admin serialization and backup payload helpers.
- `db/` - database URL validation, engine options, schema maintenance, seeding, and transaction helpers.
- `frontend/` - admin login/Flask-Admin templates and admin JavaScript assets.
- `middleware/` - admin URL authentication middleware.
- `models/` - SQLAlchemy database object and admin-managed models.
- `routes/` - admin route modules.
- `services/` - reserved for admin-only service modules when more admin logic is extracted.
- `static/` - admin-only static CSS served by the admin blueprint.

The public website should call the admin API instead of reading admin database tables directly. In this repository, `services/dashboard_api.py` is intentionally kept outside `admin/` because it is the website-side client used by `/track` to call the admin API.
