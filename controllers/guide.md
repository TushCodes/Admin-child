# Controllers module guide

This folder contains small helpers that prepare data before routes send it back to the browser.

## File purposes

- `__init__.py` gathers the most commonly used controller helpers in one import place.
- `backup.py` turns database rows into a safe backup file.
- `consignment_controller.py` keeps old imports working after the admin screens moved to Flask-Admin.
- `pagination.py` splits long database lists into pages.
- `responses.py` creates consistent JSON success and error messages.
- `serializers.py` turns consignment records into simple values that templates and APIs can use.
- `guide.md` is this plain-language guide to the controllers module.
