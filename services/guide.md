# Website services module guide

This folder contains website-owned service integrations. Admin-owned database, import/export, POD, and logistics services live under `admin/services/` so the admin panel can be moved as one folder.

## File purposes

- `__init__.py` marks this folder as the website services module.
- `dashboard_api.py` is the website-side client for `/track` calls to the admin API.
- `guide.md` is this plain-language guide to the services module.
