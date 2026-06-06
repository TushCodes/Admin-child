# Database module guide

This folder controls how the app connects to the database, starts and ends database work, and fills local development data.

## File purposes

- `__init__.py` marks this folder as the database module.
- `config.py` reads database settings and chooses safe connection options.
- `maintenance.py` creates or updates database tables that the app needs.
- `seed.py` adds sample consignments for local development when the database is mostly empty.
- `session.py` manages database transactions so changes are saved or rolled back safely.
- `guide.md` is this plain-language guide to the database module.
