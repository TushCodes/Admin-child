"""Main website routes for the home, about, and contact pages."""

import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import cache
from app import limiter
from app.admin.models import Lead
import re
from app.admin.db.session import request_session, rollback_request_session

logger = logging.getLogger(__name__)


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@cache.cached(timeout=300)
def index():
    """Render the public home page."""
    return render_template("main/index.html")


@main_bp.route("/about")
@cache.cached(timeout=300)
def about():
    """Render the company about page."""
    return render_template("main/about.html")


@main_bp.route("/contact", methods=["GET", "POST"])
@limiter.limit("10 per minute", methods=["POST"])
def contact():
    """Show the contact form and save valid messages as leads."""
    if request.method == "POST":
        try:
            source = request.form.get("source", "").strip().lower()
            return_to_homepage = source == "homepage"

            def _redirect_after_submit():
                if return_to_homepage:
                    return redirect(url_for("main.index") + "#contact")
                return redirect(url_for("main.contact"))

            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip()
            phone = request.form.get("phone", "").strip()
            subject = request.form.get("subject", "").strip()
            message = request.form.get("message", "").strip()

            if not name or not email or not phone or not message:
                flash("Please fill in all required fields.", "error")
                if return_to_homepage:
                    return _redirect_after_submit()
                return render_template("main/contact.html")

            email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(email_pattern, email):
                flash("Please enter a valid email address.", "error")
                if return_to_homepage:
                    return _redirect_after_submit()
                return render_template("main/contact.html")

            try:
                lead = Lead(
                    name=name,
                    email=email,
                    phone=phone,
                    subject=subject,
                    message=message,
                )
                request_session().add(lead)
                logger.info("Contact lead saved to database for %s", email)
            except Exception as e:
                rollback_request_session()
                logger.error(f"Failed to save contact lead: {e}")
                flash(
                    "There was an issue submitting your message. Please try again.",
                    "error",
                )
                if return_to_homepage:
                    return _redirect_after_submit()
                return render_template("main/contact.html")

            flash("Message sent successfully! We'll get back to you soon.", "success")
            return _redirect_after_submit()

        except Exception as e:
            logger.error(f"Unexpected error in contact form: {e}")
            flash("An unexpected error occurred. Please try again later.", "error")
            if request.form.get("source", "").strip().lower() == "homepage":
                return redirect(url_for("main.index") + "#contact")
            return render_template("main/contact.html")

    return render_template("main/contact.html")
