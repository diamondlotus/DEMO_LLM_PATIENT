"""
Authentication service routers with PostgreSQL integration
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List, Optional
import jwt
from datetime import datetime, timedelta
import bcrypt
import sys
import os
import uuid

# Add project root to path to import shared models and database
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from shared.models import (
    User, UserCreate, UserLogin, Token, PermissionCheck,
    UserRole, Permission
)

# Import database modules
try:
    from database.connection import get_db_session
    from database.models.user import User as DBUser
    from sqlalchemy.orm import Session
    from sqlalchemy import select
except ImportError:
    # Fallback to in-memory database if PostgreSQL is not available
    print("Warning: PostgreSQL database not available, using in-memory storage")
    from routers import router as fallback_router

router = APIRouter(prefix="/auth", tags=["authentication"])

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# JWT configuration
SECRET_KEY = "your-secret-key-here"  # Should match API Gateway
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Role-permission mapping
ROLE_PERMISSIONS = {
    UserRole.ADMIN: [perm.value for perm in Permission],
    UserRole.DOCTOR: [
        Permission.READ_USER.value,
        Permission.READ_PATIENT.value,
        Permission.CREATE_PATIENT.value,
        Permission.UPDATE_PATIENT.value,
        Permission.CREATE_APPOINTMENT.value,
        Permission.READ_APPOINTMENT.value,
        Permission.UPDATE_APPOINTMENT.value,
        Permission.CREATE_MEDICAL_RECORD.value,
        Permission.READ_MEDICAL_RECORD.value,
        Permission.UPDATE_MEDICAL_RECORD.value,
        Permission.VIEW_SCHEDULE.value,
        Permission.MANAGE_SCHEDULE.value,
    ],
    UserRole.NURSE: [
        Permission.READ_USER.value,
        Permission.READ_PATIENT.value,
        Permission.UPDATE_PATIENT.value,
        Permission.CREATE_APPOINTMENT.value,
        Permission.READ_APPOINTMENT.value,
        Permission.UPDATE_APPOINTMENT.value,
        Permission.READ_MEDICAL_RECORD.value,
        Permission.UPDATE_MEDICAL_RECORD.value,
        Permission.VIEW_SCHEDULE.value,
    ],
    UserRole.RECEPTIONIST: [
        Permission.READ_USER.value,
        Permission.READ_PATIENT.value,
        Permission.CREATE_PATIENT.value,
        Permission.UPDATE_PATIENT.value,
        Permission.CREATE_APPOINTMENT.value,
        Permission.READ_APPOINTMENT.value,
        Permission.UPDATE_APPOINTMENT.value,
        Permission.VIEW_SCHEDULE.value,
    ],
    UserRole.PATIENT: [
        Permission.READ_APPOINTMENT.value,
        Permission.READ_MEDICAL_RECORD.value,
    ],
}

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_by_username(db: Session, username: str) -> Optional[DBUser]:
    """Get user by username from database"""
    stmt = select(DBUser).where(DBUser.username == username)
    result = db.execute(stmt)
    return result.scalar_one_or_none()

def get_user_by_id(db: Session, user_id: str) -> Optional[DBUser]:
    """Get user by ID from database"""
    stmt = select(DBUser).where(DBUser.id == user_id)
    result = db.execute(stmt)
    return result.scalar_one_or_none()

def authenticate_user(db: Session, username: str, password: str) -> Optional[DBUser]:
    """Authenticate user with username and password"""
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

def check_permission(user: dict, permission: str) -> bool:
    """Check if user has a specific permission"""
    user_role = user.get("role")
    if not user_role:
        return False
    
    # Convert string role to UserRole enum
    try:
        role_enum = UserRole(user_role)
        allowed_permissions = ROLE_PERMISSIONS.get(role_enum, [])
        return permission in allowed_permissions
    except ValueError:
        return False

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    with get_db_session() as db:
        user = get_user_by_username(db, username)
        if user is None:
            raise credentials_exception
        
        return {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active
        }

# Routes
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint that returns JWT token"""
    with get_db_session() as db:
        user = authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "is_active": user.is_active,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            }
        }

@router.get("/users/me", response_model=User)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.post("/users", response_model=User)
async def create_user(user_data: UserCreate, current_user: dict = Depends(get_current_user)):
    """Create a new user (admin only)"""
    # Check if current user has permission to create users
    if not check_permission(current_user, Permission.CREATE_USER.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    with get_db_session() as db:
        # Check if username already exists
        existing_user = get_user_by_username(db, user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Check if email already exists
        stmt = select(DBUser).where(DBUser.email == user_data.email)
        result = db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        new_user = DBUser(
            id=uuid.uuid4(),
            username=user_data.username,
            email=user_data.email,
            password_hash=hash_password(user_data.password),
            full_name=user_data.full_name,
            role=user_data.role,
            is_active=user_data.is_active,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {
            "id": str(new_user.id),
            "username": new_user.username,
            "email": new_user.email,
            "full_name": new_user.full_name,
            "role": new_user.role,
            "is_active": new_user.is_active,
            "created_at": new_user.created_at,
            "updated_at": new_user.updated_at
        }

@router.get("/users", response_model=List[User])
async def get_users(current_user: dict = Depends(get_current_user)):
    """Get all users (admin only)"""
    if not check_permission(current_user, Permission.READ_USER.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    with get_db_session() as db:
        stmt = select(DBUser)
        result = db.execute(stmt)
        users = result.scalars().all()
        
        return [
            {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "is_active": user.is_active,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            }
            for user in users
        ]

@router.post("/check-permission")
async def check_user_permission(
    permission_check: PermissionCheck,
    current_user: dict = Depends(get_current_user)
):
    """Check if user has a specific permission"""
    has_permission = check_permission(current_user, permission_check.permission)
    return {
        "user_id": permission_check.user_id,
        "permission": permission_check.permission,
        "has_permission": has_permission
    }

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "LotusHealth Auth Service"}
