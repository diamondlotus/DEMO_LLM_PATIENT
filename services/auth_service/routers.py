"""
Authentication service routers
Separate routing logic from main application
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List, Optional
import jwt
from datetime import datetime, timedelta
import bcrypt
import sys
import os

# Add project root to path to import shared models and database
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from shared.models import (
    User, UserCreate, UserLogin, Token, PermissionCheck,
    UserRole, Permission
)
from database.connection import get_db_session
from database.models.user import User as DBUser
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth", tags=["authentication"])

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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
        Permission.CREATE_PATIENT.value,
        Permission.READ_PATIENT.value,
        Permission.UPDATE_PATIENT.value,
        Permission.CREATE_APPOINTMENT.value,
        Permission.READ_APPOINTMENT.value,
        Permission.UPDATE_APPOINTMENT.value,
        Permission.VIEW_SCHEDULE.value,
    ],
    UserRole.PATIENT: [
        Permission.READ_USER.value,
        Permission.READ_PATIENT.value,
        Permission.UPDATE_PATIENT.value,
        Permission.READ_APPOINTMENT.value,
        Permission.VIEW_SCHEDULE.value,
    ]
}

# Mock database (replace with real database in production)
users_db = {
    "admin1": {
        "id": "admin1",
        "username": "admin",
        "email": "admin@lotushealth.com",
        "full_name": "System Administrator",
        "role": UserRole.ADMIN,
        "password_hash": bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()),
        "is_active": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    },
    "doctor1": {
        "id": "doctor1",
        "username": "dr.smith",
        "email": "dr.smith@lotushealth.com",
        "full_name": "Dr. John Smith",
        "role": UserRole.DOCTOR,
        "password_hash": bcrypt.hashpw("doctor123".encode(), bcrypt.gensalt()),
        "is_active": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    },
    "nurse1": {
        "id": "nurse1",
        "username": "nurse.jones",
        "email": "nurse.jones@lotushealth.com",
        "full_name": "Nurse Sarah Jones",
        "role": UserRole.NURSE,
        "password_hash": bcrypt.hashpw("nurse123".encode(), bcrypt.gensalt()),
        "is_active": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
}

# Helper functions
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: bytes) -> bool:
<<<<<<< HEAD
=======
    # hashed_password is stored as bytes
>>>>>>> fa748d05b9c5aa7dd7d25d00c5cb5fd2fdc1de7a
    return bcrypt.checkpw(plain_password.encode(), hashed_password)

def get_user(username: str) -> Optional[dict]:
    for user in users_db.values():
        if user["username"] == username:
            return user
    return None

def authenticate_user(username: str, password: str) -> Optional[dict]:
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    return user

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user

def check_permission(user: dict, required_permission: str) -> bool:
    user_role = user["role"]
    if user_role not in ROLE_PERMISSIONS:
        return False
    return required_permission in ROLE_PERMISSIONS[user_role]

# Routes
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 1800,  # 30 minutes in seconds
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"],
            "is_active": user["is_active"],
            "created_at": user["created_at"],
            "updated_at": user["updated_at"]
        }
    }

@router.get("/users/me", response_model=User)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return {
        "id": current_user["id"],
        "username": current_user["username"],
        "email": current_user["email"],
        "full_name": current_user["full_name"],
        "role": current_user["role"],
        "is_active": current_user["is_active"],
        "created_at": current_user["created_at"],
        "updated_at": current_user["updated_at"]
    }

@router.post("/users", response_model=User)
async def create_user(user_data: UserCreate, current_user: dict = Depends(get_current_user)):
    # Check if current user has permission to create users
    if not check_permission(current_user, Permission.CREATE_USER.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if username already exists
    if any(user["username"] == user_data.username for user in users_db.values()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create new user
    new_user_id = f"user_{len(users_db) + 1}"
    new_user = {
        "id": new_user_id,
        "username": user_data.username,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "role": user_data.role,
        "password_hash": bcrypt.hashpw(user_data.password.encode(), bcrypt.gensalt()),
        "is_active": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    users_db[new_user_id] = new_user
    
    return {
        "id": new_user["id"],
        "username": new_user["username"],
        "email": new_user["email"],
        "full_name": new_user["full_name"],
        "role": new_user["role"],
        "is_active": new_user["is_active"],
        "created_at": new_user["created_at"],
        "updated_at": new_user["updated_at"]
    }

@router.post("/check-permission")
async def check_user_permission(
    permission_check: PermissionCheck,
    current_user: dict = Depends(get_current_user)
):
    has_permission = check_permission(current_user, permission_check.permission)
    return {
        "user_id": permission_check.user_id,
        "permission": permission_check.permission,
        "has_permission": has_permission
    }

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "LotusHealth Auth Service"}
