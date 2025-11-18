"""
User Management Service
"""
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func
from fastapi import HTTPException, status

from app.models.auth_models import User, Role
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash


class UserService:
    """Service for user management operations"""
    
    @staticmethod
    def get_users(
        db: Session,
        search: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_superuser: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[User], int]:
        """
        Get paginated list of users with filters
        Returns: (users, total_count)
        """
        query = db.query(User).options(joinedload(User.roles))
        
        # Apply filters
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                or_(
                    User.username.ilike(search_filter),
                    User.email.ilike(search_filter),
                    User.full_name.ilike(search_filter)
                )
            )
        
        if role:
            query = query.join(User.roles).filter(Role.name == role)
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        if is_superuser is not None:
            query = query.filter(User.is_superuser == is_superuser)
        
        # Get total count
        total = query.count()
        
        # Apply sorting
        sort_column = getattr(User, sort_by, User.created_at)
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Apply pagination
        offset = (page - 1) * page_size
        users = query.offset(offset).limit(page_size).all()
        
        return users, total
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID with roles"""
        return db.query(User).options(joinedload(User.roles)).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Create a new user"""
        # Check if username exists
        if UserService.get_user_by_username(db, user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        # Check if email exists
        if UserService.get_user_by_email(db, user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        
        # Create user
        user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=get_password_hash(user_data.password),
            is_active=user_data.is_active,
            is_superuser=user_data.is_superuser
        )
        
        # Assign roles if provided
        if user_data.role_ids:
            roles = db.query(Role).filter(Role.id.in_(user_data.role_ids)).all()
            if len(roles) != len(user_data.role_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="One or more role IDs are invalid"
                )
            user.roles = roles
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_data: UserUpdate) -> User:
        """Update user information"""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check email uniqueness if email is being updated
        if user_data.email and user_data.email != user.email:
            existing_user = UserService.get_user_by_email(db, user_data.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists"
                )
            user.email = user_data.email
        
        # Update fields
        if user_data.full_name is not None:
            user.full_name = user_data.full_name
        
        if user_data.is_active is not None:
            user.is_active = user_data.is_active
        
        if user_data.is_superuser is not None:
            user.is_superuser = user_data.is_superuser
        
        if user_data.password:
            user.hashed_password = get_password_hash(user_data.password)
        
        # Update roles if provided
        if user_data.role_ids is not None:
            roles = db.query(Role).filter(Role.id.in_(user_data.role_ids)).all()
            if len(roles) != len(user_data.role_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="One or more role IDs are invalid"
                )
            user.roles = roles
        
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Delete a user"""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        db.delete(user)
        db.commit()
        
        return True
    
    @staticmethod
    def assign_roles(db: Session, user_id: int, role_ids: List[int]) -> User:
        """Assign roles to user (replaces existing roles)"""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get roles
        roles = db.query(Role).filter(Role.id.in_(role_ids)).all()
        if len(roles) != len(role_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more role IDs are invalid"
            )
        
        # Replace roles
        user.roles = roles
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def add_roles(db: Session, user_id: int, role_ids: List[int]) -> User:
        """Add roles to user (keeps existing roles)"""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get new roles
        new_roles = db.query(Role).filter(Role.id.in_(role_ids)).all()
        if len(new_roles) != len(role_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more role IDs are invalid"
            )
        
        # Add new roles (avoid duplicates)
        existing_role_ids = {role.id for role in user.roles}
        for role in new_roles:
            if role.id not in existing_role_ids:
                user.roles.append(role)
        
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def remove_roles(db: Session, user_id: int, role_ids: List[int]) -> User:
        """Remove roles from user"""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Remove roles
        user.roles = [role for role in user.roles if role.id not in role_ids]
        
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def get_user_stats(db: Session) -> dict:
        """Get user statistics"""
        total_users = db.query(func.count(User.id)).scalar()
        active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar()
        superusers = db.query(func.count(User.id)).filter(User.is_superuser == True).scalar()
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": total_users - active_users,
            "superusers": superusers
        }
