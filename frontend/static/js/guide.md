# Frontend JavaScript guide

- `index.js` bootstraps shared frontend modules after DOM ready.
- `core/api-client.js`, `core/storage.js`, and `core/toast.js` provide shared API, persistence, and notification primitives.
- `core/popup-manager.js` handles hash-based popup overlays and scroll locking.
- `features/contact-form.js`, `features/form-validation.js`, and `features/chat-widget.js` provide shared form handling, validation feedback, and optional contact-widget loading.
- `index-page.js` contains home-page-only stats, focus treatment, and slider behavior.
- `menu.js`, `track.js`, and the admin scripts remain scoped to their respective experiences.
