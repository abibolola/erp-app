from app.models.base import Base
from app.db.session import engine
# delete the import above after setting up Alembic

from app.db.session import SessionLocal
from app.core.config import settings
from app.db.seeds import seed_crm, seed_leads, seed_superuser, seed_users

def seed_all():
    db = SessionLocal()
    
    # TODO: Remove this after Alembic is fully set up
    Base.metadata.create_all(bind=engine)
    try:
        seed_crm.seed_crm(db)
        seed_leads.seed_leads(db)
        
        if settings.ENV == "development":
            seed_users.seed_test_user()
            seed_superuser.seed_superuser()
        print("✅ All module seeds completed.")
    except Exception as e:
        db.rollback()
        print("❌ Seeding failed:", str(e))
    finally:
        db.close()

if __name__ == "__main__":
    seed_all()