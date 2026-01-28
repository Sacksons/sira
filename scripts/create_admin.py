#!/usr/bin/env python3
"""
Create admin user for SIRA Platform
Run from backend directory: python ../scripts/create_admin.py
"""

import sys
import os
from getpass import getpass

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import from app
from app.core.database import Base
from app.core.security import hash_password
from app.core.config import settings
from app.models.user import User


def create_admin_user():
    """Create an admin user interactively"""

    print("=" * 60)
    print("SIRA Platform - Admin User Creation")
    print("=" * 60)
    print()

    # Get user input
    username = input("Enter admin username (default: admin): ").strip() or "admin"
    email = input("Enter admin email (default: admin@sira.com): ").strip() or "admin@sira.com"

    while True:
        password = getpass("Enter admin password (min 8 characters): ")
        if len(password) < 8:
            print("Password must be at least 8 characters long!")
            continue

        confirm_password = getpass("Confirm admin password: ")
        if password != confirm_password:
            print("Passwords don't match!")
            continue
        break

    print()
    print("Creating admin user...")

    try:
        # Create engine and session
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(bind=engine)

        # Ensure tables exist
        Base.metadata.create_all(bind=engine)

        db = SessionLocal()

        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            print()
            print(f"User with username '{username}' or email '{email}' already exists!")
            db.close()
            return False

        # Create admin user
        admin = User(
            username=username,
            email=email,
            hashed_password=hash_password(password),
            role="admin",
            is_active=True,
            is_verified=True
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print()
        print("Admin user created successfully!")
        print()
        print("User Details:")
        print(f"  ID:       {admin.id}")
        print(f"  Username: {admin.username}")
        print(f"  Email:    {admin.email}")
        print(f"  Role:     {admin.role}")
        print()
        print("You can now login with these credentials!")
        print()

        db.close()
        return True

    except Exception as e:
        print()
        print(f"Error creating admin user: {e}")
        print()
        print("Please check:")
        print("  1. PostgreSQL is running")
        print("  2. Database exists and is accessible")
        print("  3. DATABASE_URL is correct in .env file")
        return False


if __name__ == "__main__":
    try:
        success = create_admin_user()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(1)
