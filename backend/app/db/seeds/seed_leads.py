from app.db.session import SessionLocal
from app.models.lead import Lead

def seed_leads(db):
    # ⚠️ WARNING: This deletes all leads. Remove or comment this out in production!
    db.query(Lead).delete()

    # ⚠️ WARNING: This is sample data. Replace or remove for production use.
    sample_leads = [
        Lead(name="Alice Smith", email="alice@example.com", phone="08012345678", status="new", notes="Requested demo", created_by_id=1),
        Lead(name="Bob Johnson", email="bob@example.com", phone="08087654321", status="contacted", notes="Sent brochure", created_by_id=1),
    ]

    db.add_all(sample_leads)
    db.commit()
    db.close()

    print("✅ Seeded test leads.")
