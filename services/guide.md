# Services module guide

This folder contains business rules and reusable workflows that should not live directly inside routes or templates.

## File purposes

- `__init__.py` marks this folder as the services module.
- `consignment_importer.py` imports consignments from Excel and exports consignments back to Excel.
- `consignment_repo.py` performs common consignment database lookups and changes.
- `consignment_service.py` validates and saves consignment changes for higher-level callers.
- `logistics.py` cleans and checks logistics values such as consignment numbers, statuses, pincodes, and coordinates.
- `pdf_export.py` creates a PDF report from consignment rows.
- `pod_storage.py` saves, deletes, and links proof-of-delivery files in cloud storage or local storage.
- `guide.md` is this plain-language guide to the services module.
