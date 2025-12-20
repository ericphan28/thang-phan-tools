#!/usr/bin/env python3
"""Seed or update custom user account"""

from app.core.database import SessionLocal
from app.models.models import User
from app.core.security import get_password_hash

def create_or_update_user():
    """Create or update user: cym_sunset@yahoo.com"""
    db = SessionLocal()
    try:
        email = "cym_sunset@yahoo.com"
        username = "cym_sunset"
        password = "Tnt@9961266"
        
        # Check if user exists by email
        user = db.query(User).filter(User.email == email).first()
        
        if user:
            # Update existing user
            print(f"⚠️  User with email '{email}' already exists. Updating...")
            user.hashed_password = get_password_hash(password)
            user.username = username
            user.is_active = True
            user.is_superuser = True  # Grant admin rights
            db.commit()
            print("✅ User updated successfully!")
        else:
            # Create new user
            print(f"Creating new user with email '{email}'...")
            new_user = User(
                username=username,
                email=email,
                hashed_password=get_password_hash(password),
                full_name="CYM Sunset",
                is_active=True,
                is_superuser=True  # Grant admin rights
            )
            db.add(new_user)
            db.commit()
            print("✅ User created successfully!")
        
        print("\n" + "="*60)
        print("📧 LOGIN CREDENTIALS:")
        print("="*60)
        print(f"   Email:    {email}")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print(f"   Role:     Super Admin")
        print("="*60)
        print("\n🌐 Login URL:")
        print("   Local:      http://localhost:5173")
        print("   Production: http://165.99.59.47")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🔐 CREATING/UPDATING CUSTOM USER")
    print("="*60 + "\n")
    create_or_update_user()
