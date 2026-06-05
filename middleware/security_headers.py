"""HTTP security header middleware."""

from flask import current_app, request


def build_content_security_policy() -> str:
    """Build the application's baseline Content Security Policy."""
    allowed_origins = current_app.config.get("CORS_ALLOWED_ORIGINS", ())
    connect_sources = ["'self'"]
    connect_sources.extend(origin for origin in allowed_origins if origin != "*")
    connect_src = " ".join(connect_sources)

    return (
        "default-src 'self'; "
        "base-uri 'self'; "
        "object-src 'none'; "
        "frame-ancestors 'self'; "
        "form-action 'self'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data: https://fonts.gstatic.com; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com; "
        f"connect-src {connect_src}; "
        "frame-src 'self' https://www.google.com https://maps.google.com;"
    )


def register_security_headers_middleware(app):
    """Register response middleware that applies safe default security headers."""

    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        response.headers.setdefault(
            "Referrer-Policy", "strict-origin-when-cross-origin"
        )
        response.headers.setdefault(
            "Permissions-Policy",
            "camera=(), microphone=(), geolocation=(), payment=(), usb=()",
        )
        response.headers.setdefault(
            "Content-Security-Policy", build_content_security_policy()
        )

        if (
            request.is_secure
            or request.headers.get("X-Forwarded-Proto", "").lower() == "https"
        ):
            response.headers.setdefault(
                "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
            )

        return response
