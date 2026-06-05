# Admin module guide

This folder powers the private admin area that staff use to sign in, review data, update consignments, import/export files, and download backups.

## File purposes

- `__init__.py` keeps older admin links working and sends visitors to the current admin screens.
- `auth.py` checks the admin username and password and remembers whether the current browser session is signed in.
- `flask_admin_setup.py` builds the admin dashboard, consignment manager, lead manager, file import/export actions, and backup download screen.
- `README.md` explains how admin authentication is configured.
- `guide.md` is this plain-language guide to the admin module.
