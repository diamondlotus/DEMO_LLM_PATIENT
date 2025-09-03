"""
Simple Authentication service routers with PostgreSQL integration
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

# Add project root to path to import shared models
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from shared.models import (
    User, UserCreate, UserUpdate, UserLogin, Token, PermissionCheck,
    UserRole, Permission
)

# Simple database connection without complex models
import psycopg2
from psycopg2.extras import RealDictCursor

router = APIRouter(prefix="/auth", tags=["authentication"])

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# JWT configuration
SECRET_KEY = "your-secret-key-here"
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

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'postgres'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'lotushealth'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'password')
    )

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

def get_user_by_username(username: str) -> Optional[dict]:
    """Get user by username from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return dict(user) if user else None
    except Exception as e:
        print(f"Database error: {e}")
        return None

def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Authenticate user with username and password"""
    user = get_user_by_username(username)
    if not user:
        return None
    if not verify_password(password, user['password_hash']):
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
    
    user = get_user_by_username(username)
    if user is None:
        raise credentials_exception
    
    return {
        "id": str(user['id']),
        "username": user['username'],
        "email": user['email'],
        "full_name": user['full_name'],
        "role": user['role'],
        "is_active": user['is_active']
    }

# Routes
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint that returns JWT token"""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user['username']}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": str(user['id']),
            "username": user['username'],
            "email": user['email'],
            "first_name": user['first_name'],
            "last_name": user['last_name'],
            "full_name": user['full_name'],
            "role": user['role'],
            "is_active": user['is_active'],
            "created_at": user['created_at'],
            "updated_at": user['updated_at']
        }
    }

@router.get("/users/me", response_model=User)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    # Get full user data from database
    user = get_user_by_username(current_user['username'])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": str(user['id']),
        "username": user['username'],
        "email": user['email'],
        "full_name": user['full_name'],
        "role": user['role'],
        "is_active": user['is_active'],
        "created_at": user['created_at'],
        "updated_at": user['updated_at']
    }

@router.get("/users", response_model=List[User])
async def get_users(current_user: dict = Depends(get_current_user)):
    """Get all users (admin only)"""
    if not check_permission(current_user, Permission.READ_USER.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [
            {
                "id": str(user['id']),
                "username": user['username'],
                "email": user['email'],
                "first_name": user['first_name'],
                "last_name": user['last_name'],
                "full_name": user['full_name'],
                "role": user['role'],
                "is_active": user['is_active'],
                "created_at": user['created_at'],
                "updated_at": user['updated_at']
            }
            for user in users
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str, current_user: dict = Depends(get_current_user)):
    """Get user by ID (admin only)"""
    if not check_permission(current_user, Permission.READ_USER.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "id": str(user['id']),
            "username": user['username'],
            "email": user['email'],
            "first_name": user['first_name'],
            "last_name": user['last_name'],
            "full_name": user['full_name'],
            "role": user['role'],
            "is_active": user['is_active'],
            "created_at": user['created_at'],
            "updated_at": user['updated_at']
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/register", response_model=User)
async def register_user(user_data: UserCreate):
    """Register a new user (public endpoint)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Check if username or email already exists
        cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (user_data.username, user_data.email))
        existing_user = cursor.fetchone()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username or email already exists")

        # Generate new user ID
        user_id = str(uuid.uuid4())

        # Hash password
        hashed_password = hash_password(user_data.password)

        # Insert user
        cursor.execute("""
            INSERT INTO users (id, username, email, first_name, last_name, full_name, password_hash, role, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (
            user_id,
            user_data.username,
            user_data.email,
            user_data.first_name,
            user_data.last_name,
            user_data.full_name,
            hashed_password,
            user_data.role.value if hasattr(user_data.role, 'value') else user_data.role,
            user_data.is_active if user_data.is_active is not None else True
        ))

        user = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        return {
            "id": str(user['id']),
            "username": user['username'],
            "email": user['email'],
            "first_name": user['first_name'],
            "last_name": user['last_name'],
            "full_name": user['full_name'],
            "role": user['role'],
            "is_active": user['is_active'],
            "created_at": user['created_at'],
            "updated_at": user['updated_at']
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error registering user: {str(e)}")

@router.post("/users", response_model=User)
async def create_user(user_data: UserCreate, current_user: dict = Depends(get_current_user)):
    """Create a new user (admin only)"""
    if not check_permission(current_user, Permission.CREATE_USER.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if username or email already exists
        cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (user_data.username, user_data.email))
        existing_user = cursor.fetchone()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username or email already exists")
        
        # Generate new user ID
        user_id = str(uuid.uuid4())
        
        # Hash password
        hashed_password = hash_password(user_data.password)
        
        # Insert user
        cursor.execute("""
            INSERT INTO users (id, username, email, first_name, last_name, full_name, password_hash, role, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (
            user_id,
            user_data.username,
            user_data.email,
            user_data.first_name,
            user_data.last_name,
            user_data.full_name,
            hashed_password,
            user_data.role.value if hasattr(user_data.role, 'value') else user_data.role,
            user_data.is_active if user_data.is_active is not None else True
        ))
        
        user = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "id": str(user['id']),
            "username": user['username'],
            "email": user['email'],
            "first_name": user['first_name'],
            "last_name": user['last_name'],
            "full_name": user['full_name'],
            "role": user['role'],
            "is_active": user['is_active'],
            "created_at": user['created_at'],
            "updated_at": user['updated_at']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

@router.put("/users/{user_id}", response_model=User)
async def update_user(user_id: str, user_data: UserUpdate, current_user: dict = Depends(get_current_user)):
    """Update user (admin only)"""
    if not check_permission(current_user, Permission.UPDATE_USER.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Build update query dynamically
        update_fields = []
        values = []
        
        for field, value in user_data.dict(exclude_unset=True).items():
            if field == 'password':
                # Hash password if provided
                update_fields.append("password_hash = %s")
                values.append(hash_password(value))
            elif field == 'role':
                # Convert role enum to string
                update_fields.append("role = %s")
                values.append(value.value if hasattr(value, 'value') else value)
            else:
                update_fields.append(f"{field} = %s")
                values.append(value)
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        values.append(user_id)
        
        cursor.execute(f"""
            UPDATE users 
            SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING *
        """, values)
        
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "id": str(user['id']),
            "username": user['username'],
            "email": user['email'],
            "first_name": user['first_name'],
            "last_name": user['last_name'],
            "full_name": user['full_name'],
            "role": user['role'],
            "is_active": user['is_active'],
            "created_at": user['created_at'],
            "updated_at": user['updated_at']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")

@router.delete("/users/{user_id}")
async def delete_user(user_id: str, current_user: dict = Depends(get_current_user)):
    """Delete user (admin only)"""
    if not check_permission(current_user, Permission.DELETE_USER.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="User not found")
        
        # Soft delete by setting is_active to false
        cursor.execute("UPDATE users SET is_active = false, updated_at = CURRENT_TIMESTAMP WHERE id = %s", (user_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"message": "User deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")

@router.post("/refresh")
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """Refresh JWT token"""
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user['username']}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": current_user
    }

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
