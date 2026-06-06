# Routes module guide

This folder connects public website addresses to Python functions that render pages or handle visitor form submissions. Admin routes live under `admin/routes/` and `admin/api/`.

## File purposes

- `__init__.py` marks this folder as the website routes module.
- `main.py` handles the home, about, and contact pages.
- `pages.py` renders service pages from matching templates.
- `track.py` handles shipment tracking searches and POD downloads through the admin API client.
- `guide.md` is this plain-language guide to the routes module.
