# Frontend guide

This folder has the public website code that the browser uses. Going forward, treat this frontend as maintenance work: small fixes, clear comments, and no big migrations unless specifically planned.

## Where code lives

- `templates/` has Flask/Jinja HTML pages.
- `templates/layouts/` has common page layouts.
- `templates/partials/` has repeated parts like header, menu, footer, and shared scripts.
- `templates/pages/` has service pages.
- `templates/track/` has the shipment tracking page.
- `static/js/core/` has shared helpers like API calls, storage, toast messages, and popups.
- `static/js/features/` has small page features like contact form, validation, and chat widget.
- `static/js/` has page-level scripts such as menu, tracking, home page, and admin table behavior.
- `static/assets/scss/` has newer SCSS for page and component styles.
- `static/scss/` has legacy SCSS that may still be used by existing pages.

## Comment style for vendors

- Keep comments short and close to the code.
- Use simple language: explain what the code does and what page/field it belongs to.
- Mention important dependencies, like Flask data attributes, `window.App`, or admin globals.
- Do not add long technical notes unless the code is risky or confusing.
- Prefer maintenance changes over rewrites.

## Shared script order

`templates/partials/shared-scripts.html` loads shared JS in this order:

1. browser config,
2. core helpers,
3. feature scripts,
4. `static/js/index.js` to start them.
