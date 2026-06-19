"""One-off script to display seeded consignments for local dev."""

from pathlib import Path
import sys

# Ensure the parent directory of the `admin` package is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from admin import create_app

app = create_app()

with app.app_context():
    from admin.models import Consignment
    import os
    print("ENV DATABASE_URL:", os.getenv("DATABASE_URL"))
    print("app.config SQLALCHEMY_DATABASE_URI:", app.config.get("SQLALCHEMY_DATABASE_URI"))
    db_path = None
    if os.getenv("DATABASE_URL", "").startswith("sqlite://"):
        db_path = os.getenv("DATABASE_URL").replace("sqlite://", "")
        print("SQLite file exists:", os.path.exists(db_path), db_path)

    rows = Consignment.query.order_by(Consignment.id).limit(20).all()
    print(f"Total rows (first 20 shown): {len(rows)}")
    for r in rows:
        print(r.id, r.consignment_number, r.status, r.pickup_pincode, r.drop_pincode)
    # Try seeding explicitly and report any errors
    try:
        from admin.db.seed import seed_development_data

        print("Running seed_development_data...")
        seed_development_data(__import__("admin").models.db, app)
        rows = Consignment.query.order_by(Consignment.id).limit(20).all()
        print(f"After seeding: Total rows (first 20 shown): {len(rows)}")
    except Exception as e:
        import traceback

        print("Seeding failed with exception:")
        traceback.print_exc()
