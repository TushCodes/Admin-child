# Admin module guide

This folder powers the private admin area that staff use to sign in, review data, update consignments, import/export files, serve the admin API, and download backups. It can be embedded by the website app or run as its own Flask app.

## File purposes

- `app.py` creates the standalone admin Flask app and registers admin routes, middleware, database setup, and Flask-Admin views.
- `run_local.py` starts the standalone admin app on port `5001` for local development.
- `__init__.py` defines the admin blueprint and keeps older admin links pointed at the current admin screens.
- `auth.py` handles Supabase/local admin authentication and session state.
- `extensions.py` stores shared admin extension instances such as the rate limiter.
- `flask_admin_setup.py` builds the admin dashboard, consignment manager, lead manager, file import/export actions, and backup download screen.
- `README.md` explains how to run the standalone admin app and configure admin authentication.
- `PACKAGE.md` documents the extraction boundary for moving `admin/` into a separate repository.
- `guide.md` is this plain-language guide to the admin module.
