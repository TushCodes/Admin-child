from flask import redirect, request, url_for
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView

from app.admin.auth import is_admin_authenticated
from app.models import Consignment, Lead, db


class SecureModelView(ModelView):
    can_view_details = True
    page_size = 50

    def is_accessible(self):
        return is_admin_authenticated()

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("admin.login", next=request.url))


class SecureAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return is_admin_authenticated()

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("admin.login", next=request.url))


def init_flask_admin(app):
    """Initialize Flask-Admin views bound to SQLAlchemy models."""
    admin = Admin(
        app,
        name="Admin Panel",
        template_mode="bootstrap4",
        index_view=SecureAdminIndexView(url="/flask-admin"),
    )

    admin.add_view(
        SecureModelView(
            Consignment,
            db.session,
            name="Consignments",
            endpoint="consignments_admin",
            category="Operations",
            column_searchable_list=("consignment_number", "status"),
            column_filters=("status", "pickup_pincode", "drop_pincode"),
            form_excluded_columns=("eta_debug_json",),
        )
    )

    admin.add_view(
        SecureModelView(
            Lead,
            db.session,
            name="Leads",
            endpoint="leads_admin",
            category="CRM",
            can_create=False,
            can_edit=False,
            column_searchable_list=("name", "email", "phone", "subject"),
            column_default_sort=("created_at", True),
        )
    )

    return admin
