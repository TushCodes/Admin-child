# Middleware module guide

This folder contains request and response helpers that run around normal page handling to protect the app, log activity, and keep responses consistent.

## File purposes

- `__init__.py` registers all middleware in the intended order.
- `admin_auth.py` protects admin-only pages from visitors who are not signed in.
- `cors.py` controls which websites may call this app from a browser.
- `database.py` commits successful database work and rolls back failed work after each request.
- `error_handling.py` turns common failures into helpful HTML or JSON responses.
- `observability.py` configures logging and request timing information.
- `request_context.py` gives each request its own request ID for logs and troubleshooting.
- `security_headers.py` adds browser security headers to outgoing responses.
- `README.md` explains middleware order and responsibilities in more detail.
- `guide.md` is this plain-language guide to the middleware module.
