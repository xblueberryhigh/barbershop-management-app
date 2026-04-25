import os

from dotenv import load_dotenv

from app.database import SessionLocal
from app.enums import UserRole
from app.models import User
from app.security import hash_password


def main():
    load_dotenv()

    email = os.getenv("FIRST_ADMIN_EMAIL")
    password = os.getenv("FIRST_ADMIN_PASSWORD")
    first_name = os.getenv("FIRST_ADMIN_FIRST_NAME", "Admin")
    last_name = os.getenv("FIRST_ADMIN_LAST_NAME", "User")

    if not email or not password:
        raise ValueError("FIRST_ADMIN_EMAIL and FIRST_ADMIN_PASSWORD must be set")

    db = SessionLocal()
    try:
        existing_admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if existing_admin:
            print("Admin already exists. Bootstrap is no longer needed.")
            return
        
        existing_user_with_email = db.query(User).filter(User.email == email).first()
        if existing_user_with_email:
            print("A user with this email already exists. Choose another email or promote that user manually.")
            return

        new_admin = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            hashed_password=hash_password(password),
            role=UserRole.ADMIN,
        )

        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)

        print(f"Created admin: {new_admin.email}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
