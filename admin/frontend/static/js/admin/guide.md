# Admin JavaScript guide

This folder has small browser helpers for admin pages.

## Where code lives

- `api.js` talks to admin API endpoints.
- `state.js` remembers table edits before Save is clicked.
- `validation.js` checks admin form and row values.
- `guide.md` explains this folder for future vendors/maintainers.

## Comment style

- Keep comments short and practical.
- Explain which admin screen or action the code supports.
- Keep `window.adminAPI`, `window.adminState`, and `window.adminValidation` stable because other admin scripts use them.
- Do not change the no-framework style unless a future task asks for it.
