# Models module guide

This folder describes the database tables used by the app.

## File purposes

- `__init__.py` creates the shared database object and exposes the app's models.
- `base.py` stores common model behavior shared by database records.
- `consignment.py` defines shipment records that admins manage and customers track.
- `lead.py` defines contact form messages saved for staff follow-up.
- `track.py` defines the tracking-facing consignment record used by public lookup pages.
- `guide.md` is this plain-language guide to the models module.
