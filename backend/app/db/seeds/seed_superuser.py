from app.db.session import SessionLocal
from app.models.user import User
from app.services.auth_service import get_password_hash, create_access_token

def seed_superuser():
    db = SessionLocal()

    email = "admin@example.com"
    existing = db.query(User).filter(User.email == email).first()

    if not existing:
        superuser = User(
            username="admin",
            email=email,
            password_hash=get_password_hash("admin123"),
            is_active=True,
            is_superuser=True,
            org_id=1,  # Adjust if needed
        )
        db.add(superuser)
        db.commit()
        db.refresh(superuser)
        print("✅ Superuser created.")
    else:
        superuser = existing
        print("ℹ️ Superuser already exists.")

    token = create_access_token({
        "sub": superuser.username,
        "user_id": superuser.id
    })

    print("🔑 Superuser Token (use in Swagger 'Authorize'):")
    print(f"Bearer {token}")

    db.close()
