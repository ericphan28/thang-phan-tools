"""
Test Authentication System

Run: pytest backend/tests/test_auth.py -v
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.core.security import get_password_hash
from app.models.models import User, Role, Permission

# Test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override database dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Test client
client = TestClient(app)


# Setup and teardown
@pytest.fixture(scope="function")
def setup_database():
    """Create test database and tables"""
    Base.metadata.create_all(bind=engine)
    
    # Create test data
    db = TestingSessionLocal()
    
    # Create roles
    viewer_role = Role(name="viewer", description="Viewer role")
    editor_role = Role(name="editor", description="Editor role")
    admin_role = Role(name="admin", description="Admin role")
    
    db.add_all([viewer_role, editor_role, admin_role])
    db.commit()
    
    # Create permissions
    permissions = [
        Permission(role_id=admin_role.id, resource="image", action="delete"),
        Permission(role_id=editor_role.id, resource="image", action="write"),
        Permission(role_id=viewer_role.id, resource="image", action="read"),
    ]
    
    db.add_all(permissions)
    db.commit()
    
    # Create test users
    admin_user = User(
        username="test_admin",
        email="admin@test.com",
        hashed_password=get_password_hash("admin123"),
        full_name="Test Admin",
        is_active=True,
        is_superuser=True
    )
    admin_user.roles.append(admin_role)
    
    editor_user = User(
        username="test_editor",
        email="editor@test.com",
        hashed_password=get_password_hash("editor123"),
        full_name="Test Editor",
        is_active=True,
        is_superuser=False
    )
    editor_user.roles.append(editor_role)
    
    viewer_user = User(
        username="test_viewer",
        email="viewer@test.com",
        hashed_password=get_password_hash("viewer123"),
        full_name="Test Viewer",
        is_active=True,
        is_superuser=False
    )
    viewer_user.roles.append(viewer_role)
    
    db.add_all([admin_user, editor_user, viewer_user])
    db.commit()
    
    db.close()
    
    yield
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)


# ============================================================================
# TEST CASES
# ============================================================================

def test_register_user(setup_database):
    """Test user registration"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@test.com",
            "password": "Password123",
            "full_name": "New User"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["user"]["username"] == "newuser"
    assert data["user"]["email"] == "newuser@test.com"
    assert "viewer" in data["user"]["roles"]


def test_login_success(setup_database):
    """Test successful login"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "test_admin",
            "password": "admin123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "token" in data
    assert data["token"]["token_type"] == "bearer"
    assert data["user"]["username"] == "test_admin"


def test_login_wrong_password(setup_database):
    """Test login with wrong password"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "test_admin",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]


def test_get_current_user(setup_database):
    """Test getting current user info"""
    # Login first
    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "test_admin", "password": "admin123"}
    )
    token = login_response.json()["token"]["access_token"]
    
    # Get current user
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "test_admin"
    assert data["email"] == "admin@test.com"
    assert "admin" in data["roles"]


def test_unauthorized_access(setup_database):
    """Test accessing protected endpoint without token"""
    response = client.get("/api/v1/auth/me")
    
    assert response.status_code == 403  # HTTPBearer returns 403 for missing credentials


def test_change_password(setup_database):
    """Test password change"""
    # Login
    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "test_viewer", "password": "viewer123"}
    )
    token = login_response.json()["token"]["access_token"]
    
    # Change password
    response = client.post(
        "/api/v1/auth/change-password",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "old_password": "viewer123",
            "new_password": "NewPassword123"
        }
    )
    
    assert response.status_code == 200
    assert response.json()["success"] is True
    
    # Try login with new password
    new_login = client.post(
        "/api/v1/auth/login",
        json={"username": "test_viewer", "password": "NewPassword123"}
    )
    
    assert new_login.status_code == 200


def test_admin_list_users(setup_database):
    """Test admin listing all users"""
    # Login as admin
    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "test_admin", "password": "admin123"}
    )
    token = login_response.json()["token"]["access_token"]
    
    # List users
    response = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3  # At least admin, editor, viewer


def test_non_admin_cannot_list_users(setup_database):
    """Test non-admin cannot list users"""
    # Login as viewer
    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "test_viewer", "password": "viewer123"}
    )
    token = login_response.json()["token"]["access_token"]
    
    # Try to list users
    response = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]


def test_refresh_token(setup_database):
    """Test token refresh"""
    # Login
    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "test_admin", "password": "admin123"}
    )
    old_token = login_response.json()["token"]["access_token"]
    
    # Refresh token
    response = client.post(
        "/api/v1/auth/refresh",
        headers={"Authorization": f"Bearer {old_token}"}
    )
    
    assert response.status_code == 200
    new_token = response.json()["access_token"]
    assert new_token != old_token
    
    # Use new token
    user_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {new_token}"}
    )
    
    assert user_response.status_code == 200


def test_assign_roles(setup_database):
    """Test assigning roles to user"""
    # Login as admin
    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "test_admin", "password": "admin123"}
    )
    token = login_response.json()["token"]["access_token"]
    
    # Get viewer user ID
    users_response = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"}
    )
    viewer_user = next(u for u in users_response.json() if u["username"] == "test_viewer")
    
    # Assign editor role
    response = client.post(
        f"/api/v1/users/{viewer_user['id']}/roles",
        headers={"Authorization": f"Bearer {token}"},
        json=["editor", "viewer"]
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "editor" in data["roles"]
    assert "viewer" in data["roles"]


# ============================================================================
# RUN TESTS
# ============================================================================
"""
# Install pytest first
pip install pytest pytest-asyncio

# Run all tests
pytest backend/tests/test_auth.py -v

# Run specific test
pytest backend/tests/test_auth.py::test_login_success -v

# Run with coverage
pip install pytest-cov
pytest backend/tests/test_auth.py --cov=app --cov-report=html
"""
