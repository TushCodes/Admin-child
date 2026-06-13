"""Tests for dashboard data API backed public tracking."""

from pathlib import Path


def test_dashboard_data_api_requires_authentication(client):
    response = client.get(
        "/admin/api/dashboard-data", headers={"Accept": "application/json"}
    )

    assert response.status_code == 401
    assert response.get_json()["success"] is False


def test_dashboard_data_api_returns_admin_dashboard_records(app, client):
    from app.admin.models import Consignment, Lead, db

    with app.app_context():
        db.session.add(
            Consignment(
                consignment_number="API123",
                status="In Transit",
                pickup_pincode="111111",
                drop_pincode="222222",
                eta="Tomorrow",
            )
        )
        db.session.add(
            Lead(
                name="Test Lead",
                email="lead@example.com",
                phone="1234567890",
                subject="Quote",
                message="Please call back.",
            )
        )
        db.session.commit()

    with client.session_transaction() as session:
        session["admin_authenticated"] = True

    response = client.get("/admin/api/dashboard-data")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    consignment_numbers = {
        item["consignment_number"] for item in payload["data"]["consignments"]
    }
    lead_emails = {item["email"] for item in payload["data"]["leads"]}
    assert "API123" in consignment_numbers
    assert "lead@example.com" in lead_emails


def test_track_page_fetches_consignment_through_dashboard_api(app, client):
    from app.admin.models import Consignment, db

    with app.app_context():
        db.session.add(
            Consignment(
                consignment_number="TRACKAPI1",
                status="Delivered",
                pickup_tag="Origin Hub",
                pickup_pincode="111111",
                drop_tag="Destination Hub",
                drop_pincode="222222",
                eta="Delivered today",
            )
        )
        db.session.commit()

    response = client.post("/track", data={"consignment_number": "trackapi1"})

    assert response.status_code == 200
    assert b"TRACKAPI1" in response.data
    assert b"Delivered" in response.data
    assert b"Origin Hub" in response.data


def test_track_test_widget_matches_track_lookup_behavior(app, client):
    from app.admin.models import Consignment, db

    with app.app_context():
        db.session.add(
            Consignment(
                consignment_number="WIDGETAPI1",
                status="In Transit",
                pickup_tag="Widget Origin",
                pickup_pincode="333333",
                drop_tag="Widget Destination",
                drop_pincode="444444",
                eta="Tomorrow",
            )
        )
        db.session.commit()

    response = client.post(
        "/track-test-widget", data={"consignment_number": "widgetapi1"}
    )

    assert response.status_code == 200
    assert b"WIDGETAPI1" in response.data
    assert b"In Transit" in response.data
    assert b"Widget Origin" in response.data
    assert b"Widget Destination" in response.data


def test_track_pod_uses_dashboard_api_for_consignment_data(app, client):
    from app.admin.models import Consignment, db

    upload_folder = Path(app.instance_path) / "uploads"
    upload_folder.mkdir(parents=True, exist_ok=True)
    (upload_folder / "api-pod.txt").write_bytes(b"pod-through-api")

    with app.app_context():
        db.session.add(
            Consignment(
                consignment_number="PODAPI1",
                status="Delivered",
                pod_image="api-pod.txt",
            )
        )
        db.session.commit()

    response = client.get("/track/pod/PODAPI1")

    assert response.status_code == 200
    assert response.data == b"pod-through-api"
