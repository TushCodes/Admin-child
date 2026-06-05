# Middleware

Middleware is registered through `app.middleware.register_middleware(app)` during
application startup. Keep cross-cutting request/response concerns here so route
handlers can stay focused on business behavior.

## Registration order

1. `register_request_context_middleware()` sets `g.request_id` and request timing
   before handlers run, then adds `X-Request-ID` and `X-Response-Time-ms` after
   the response is produced.
2. `register_observability()` configures logging handlers with the
   request-id filter that reads the request context created above.
3. `register_admin_auth_middleware()` gates `/admin` and `/flask-admin` paths
   before they reach route handlers or Flask-Admin views.
4. `register_security_headers_middleware()` adds default security headers to
   outgoing responses.
5. `register_error_handlers()` centralizes HTML/JSON error responses and uses
   `wants_json_response()` for content negotiation.

## Responsibilities

- `request_context.py`: correlation IDs and response timing headers.
- `observability.py`: request-aware logging registration.
- `admin_auth.py`: URL-space admin authentication gates; Flask-Admin views keep
  their own `is_accessible()` checks as a defense-in-depth layer.
- `security_headers.py`: CSP, HSTS, permissions, and other response headers.
- `error_handling.py`: global error handlers for common HTTP failures and
  unexpected exceptions.
- `utils/content_negotiation.py`: shared helper for choosing JSON vs. HTML/plain-text
  responses. `middleware/response_negotiation.py` remains a compatibility shim.
