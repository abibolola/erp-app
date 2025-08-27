# backend/create_test_user.py
from app.db.session import SessionLocal
from app.models.user import User
from app.services.auth_service import get_password_hash

db = SessionLocal()

# Create test user
test_user = User(
    username="admin",
    email="admin@example.com",
    password_hash=get_password_hash("admin123"),
    org_id=1,
    role_id=1
)

db.add(test_user)
db.commit()
print("Test user created: admin@example.com / admin123")