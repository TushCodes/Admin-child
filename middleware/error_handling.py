"""Application error handlers registered as middleware-adjacent plumbing."""

import logging
import os

from flask import Response, jsonify, render_template, request
from werkzeug.exceptions import HTTPException

from app.utils.content_negotiation import wants_json_response

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    """Register global error handlers for HTML and JSON clients."""

    @app.errorhandler(404)
    def page_not_found(error):
        logger.warning("404 error: %s", request.url)
        if wants_json_response(request):
            return jsonify({"error": "Resource not found"}), 404
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        logger.error("500 error: %s", error)
        if wants_json_response(request):
            return jsonify({"error": "Internal server error"}), 500
        return render_template("errors/500.html"), 500

    @app.errorhandler(403)
    def forbidden(error):
        logger.warning("403 error: %s", request.url)
        if wants_json_response(request):
            return jsonify({"error": "Access forbidden"}), 403
        return render_template("errors/403.html"), 403

    @app.errorhandler(429)
    def rate_limited(error):
        logger.warning(
            "Rate limit exceeded for %s %s from %s",
            request.method,
            request.path,
            request.headers.get("X-Forwarded-For", request.remote_addr),
        )

        message = "Too many requests. Please try again later."
        if wants_json_response(request):
            response = jsonify({"error": message})
            response.status_code = 429
            return response

        return Response(message, status=429, mimetype="text/plain")

    @app.errorhandler(Exception)
    def handle_exception(error):
        if isinstance(error, HTTPException):
            return error

        logger.error("Unhandled exception: %s", error, exc_info=True)
        if wants_json_response(request):
            if os.getenv("FLASK_ENV", "").strip().lower() == "development":
                import traceback

                return (
                    jsonify(
                        {
                            "error": str(error) or "Exception",
                            "traceback": traceback.format_exc(),
                        }
                    ),
                    500,
                )

            return jsonify({"error": "An unexpected error occurred"}), 500

        return render_template("errors/500.html"), 500
