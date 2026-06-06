"""Tests for POD storage and serving without expiring signed URLs."""

from pathlib import Path


def test_pod_url_helper_does_not_create_signed_urls(monkeypatch):
    from app.admin.services import pod_storage

    class StorageBucket:
        def create_signed_url(self, *_args, **_kwargs):  # pragma: no cover - must not be called
            raise AssertionError("signed URLs must not be created for POD files")

        def get_public_url(self, object_path):
            return {"publicUrl": f"https://cdn.example.test/{object_path}"}

    class Storage:
        def from_(self, _bucket):
            return StorageBucket()

    class Client:
        storage = Storage()

    monkeypatch.setattr(pod_storage, "get_supabase_client", lambda: Client())

    assert (
        pod_storage.get_pod_url("supabase:pod-uploads/consignments/proof.jpg")
        == "https://cdn.example.test/consignments/proof.jpg"
    )


def test_signed_supabase_url_in_database_is_served_by_object_path(app, client, monkeypatch):
    from app.admin.models import Consignment, db
    from app.admin.services import pod_storage

    calls = []

    class StorageBucket:
        def download(self, object_path):
            calls.append(object_path)
            return b"pod-bytes"

        def create_signed_url(self, *_args, **_kwargs):  # pragma: no cover - must not be called
            raise AssertionError("signed URLs must not be created for POD files")

    class Storage:
        def from_(self, bucket):
            assert bucket == "pod-uploads"
            return StorageBucket()

    class Client:
        storage = Storage()

    monkeypatch.setattr(pod_storage, "get_supabase_client", lambda: Client())

    with app.app_context():
        consignment = Consignment(
            consignment_number="PODSIGNED1",
            status="Delivered",
            pod_image=(
                "https://example.supabase.co/storage/v1/object/sign/"
                "pod-uploads/consignments/proof.jpg?token=expired"
            ),
        )
        db.session.add(consignment)
        db.session.commit()
        consignment_id = consignment.id

    with client.session_transaction() as session:
        session["admin_authenticated"] = True

    response = client.get(f"/flask-admin/consignments_admin/{consignment_id}/pod")

    assert response.status_code == 200
    assert response.data == b"pod-bytes"
    assert calls == ["consignments/proof.jpg"]


def test_public_track_pod_serves_local_database_file(app, client):
    from app.admin.models import Consignment, db

    upload_folder = Path(app.instance_path) / "uploads"
    upload_folder.mkdir(parents=True, exist_ok=True)
    (upload_folder / "permanent-pod.txt").write_bytes(b"local-pod")

    with app.app_context():
        db.session.add(
            Consignment(
                consignment_number="PODLOCAL1",
                status="Delivered",
                pod_image="permanent-pod.txt",
            )
        )
        db.session.commit()

    response = client.get("/track/pod/PODLOCAL1")

    assert response.status_code == 200
    assert response.data == b"local-pod"
    assert response.headers["Content-Disposition"].startswith("inline")
