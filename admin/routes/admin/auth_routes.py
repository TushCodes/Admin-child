"""Admin authentication routes for login and logout."""

import logging

from flask import redirect, render_template, request, url_for

from app import limiter
from app.admin import admin_bp
from app.admin.auth import (
    AdminAuthenticationError,
    authenticate_admin,
    get_admin_auth_provider,
    is_admin_authenticated,
    login_admin,
    logout_admin,
)

logger = logging.getLogger(__name__)


@admin_bp.route("/admin/login", methods=["GET"])
def login():
    """Render the admin login form."""
    if is_admin_authenticated():
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/login.html", error=None)


@admin_bp.route("/admin/login", methods=["POST"])
@limiter.limit("5 per minute")
def login_submit():
    """Process the admin login form."""
    if is_admin_authenticated():
        return redirect(url_for("admin.dashboard"))

    error = None

    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""

    try:
        auth_result = authenticate_admin(username, password)
    except AdminAuthenticationError:
        logger.exception("Admin authentication is not configured correctly")
        error = "Admin authentication is not configured. Please check Supabase settings."
        return render_template("admin/login.html", error=error)

    if auth_result:
        login_admin(auth_result=auth_result)
        logger.info(
            "Admin login successful for user: %s via %s",
            auth_result.username,
            auth_result.provider,
        )
        return redirect(url_for("admin.dashboard"))

    logger.warning(
        "Failed admin login attempt for username: %s via %s",
        username,
        get_admin_auth_provider(),
    )
    error = "Invalid email or password."

    return render_template("admin/login.html", error=error)


@admin_bp.route("/admin/logout", methods=["GET"])
@limiter.limit("10 per minute")
def logout():
    """Clear admin session and redirect to the login page."""
    logout_admin()
    logger.info("Admin logged out.")
    return redirect(url_for("admin.login"))
