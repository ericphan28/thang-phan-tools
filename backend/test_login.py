"""
Test authentication login directly
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.security import verify_password, create_access_token
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# SQLite
engine = create_engine("sqlite:///./utility.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

# Recreate minimal User model for SQLite
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta

Base = declarative_base()

user_roles = Table(
    'user_roles', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String)
    hashed_password = Column(String)
    full_name = Column(String)
    is_active = Column(Boolean)
    is_superuser = Column(Boolean)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    roles = relationship("Role", secondary=user_roles, back_populates="users")

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    created_at = Column(DateTime)
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", back_populates="role")

class Permission(Base):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey('roles.id'))
    resource = Column(String)
    action = Column(String)
    created_at = Column(DateTime)
    role = relationship("Role", back_populates="permissions")

# Test login
def test_login():
    db = SessionLocal()
    try:
        # Find user
        user = db.query(User).filter(User.username == "admin").first()
        
        if not user:
            print("❌ User 'admin' not found!")
            return
        
        print(f"✅ Found user: {user.username} ({user.email})")
        print(f"   Active: {user.is_active}")
        print(f"   Superuser: {user.is_superuser}")
        
        # Verify password
        password_ok = verify_password("admin123", user.hashed_password)
        print(f"   Password verify: {password_ok}")
        
        if password_ok:
            # Get roles
            roles = [role.name for role in user.roles]
            print(f"   Roles: {roles}")
            
            # Create token
            token = create_access_token(
                data={
                    "user_id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "roles": roles,
                    "is_superuser": user.is_superuser
                },
                expires_delta=timedelta(minutes=1440)
            )
            
            print(f"\n🎉 LOGIN SUCCESS!")
            print(f"Token: {token[:50]}...")
            print(f"\nTest this token:")
            print(f'curl -H "Authorization: Bearer {token}" http://localhost:8000/api/v1/auth/me')
            
    finally:
        db.close()

if __name__ == "__main__":
    test_login()
