# Admin authentication

Admin authentication is split by responsibility:

- `app.middleware.admin_auth` protects the `/admin` and `/flask-admin` URL spaces
  before requests reach route handlers.
- `admin/auth.py` owns session state and credential validation helpers.
- Flask-Admin `is_accessible()` hooks remain in `admin/flask_admin_setup.py` as a
  defense-in-depth check for model and index views.

The older route-decorator style `require_admin()` helper is intentionally not
present. New admin endpoints should rely on the middleware gate for URL-space
protection and call `is_admin_authenticated()` only when they need an explicit
in-handler check.
