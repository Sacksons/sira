#!/usr/bin/env python3
"""
Create initial admin user for SIRA Platform
Usage: python create_admin.py
"""

import os
import sys
from getpass import getpass

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.core.security import hash_password
from app.core.database import Base
from app.core.config import settings


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
        if settings.DATABASE_URL.startswith("sqlite"):
            engine = create_engine(
                settings.DATABASE_URL,
                connect_args={"check_same_thread": False}
            )
        else:
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
            is_active=True
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
        print("Get access token:")
        print(f'  curl -X POST "http://localhost:8000/api/v1/auth/login" \\')
        print(f'    -H "Content-Type: application/x-www-form-urlencoded" \\')
        print(f'    -d "username={username}&password=YOUR_PASSWORD"')
        print()

        db.close()
        return True

    except Exception as e:
        print()
        print(f"Error creating admin user: {e}")
        print()
        print("Please check:")
        print("  1. Database is configured correctly")
        print("  2. DATABASE_URL is correct in .env file")
        return False


if __name__ == "__main__":
    try:
        success = create_admin_user()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(1)
