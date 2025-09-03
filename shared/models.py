"""
Shared Pydantic models for API requests/responses
These models are used across all services to ensure consistency
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# ============================================================================
# ENUMS
# ============================================================================

class UserRole(str, Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    NURSE = "nurse"
    RECEPTIONIST = "receptionist"
    PATIENT = "patient"

class Permission(str, Enum):
    # User management
    CREATE_USER = "create_user"
    READ_USER = "read_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    
    # Patient management
    CREATE_PATIENT = "create_patient"
    READ_PATIENT = "read_patient"
    UPDATE_PATIENT = "update_patient"
    DELETE_PATIENT = "delete_patient"
    
    # Appointment management
    CREATE_APPOINTMENT = "create_appointment"
    READ_APPOINTMENT = "read_appointment"
    UPDATE_APPOINTMENT = "update_appointment"
    DELETE_APPOINTMENT = "delete_appointment"
    
    # Medical records
    CREATE_MEDICAL_RECORD = "create_medical_record"
    READ_MEDICAL_RECORD = "read_medical_record"
    UPDATE_MEDICAL_RECORD = "update_medical_record"
    
    # Schedule management
    MANAGE_SCHEDULE = "manage_schedule"
    VIEW_SCHEDULE = "view_schedule"

class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class AppointmentType(str, Enum):
    OFFICE_VISIT = "office_visit"
    CONSULTATION = "consultation"
    FOLLOW_UP = "follow_up"
    EMERGENCY = "emergency"
    ROUTINE_CHECKUP = "routine_checkup"

class VisitType(str, Enum):
    NEW_PATIENT = "new_patient"
    ESTABLISHED_PATIENT = "established_patient"
    URGENT_CARE = "urgent_care"
    SPECIALIST_CONSULTATION = "specialist_consultation"

# ============================================================================
# USER MODELS
# ============================================================================

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    full_name: str = Field(..., min_length=2, max_length=100)
    role: UserRole
    is_active: bool = True

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    email: Optional[str] = Field(None, pattern=r"^[^@]+@[^@]+\.[^@]+$")
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    is_active: Optional[bool] = None

class User(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: User

class PermissionCheck(BaseModel):
    permission: str
    user_id: str

# ============================================================================
# PATIENT MODELS
# ============================================================================

class PatientBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    date_of_birth: datetime
    gender: str = Field(..., pattern=r"^(male|female|other)$")
    phone: str = Field(..., min_length=10, max_length=20)
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")
    address: str = Field(..., min_length=10, max_length=200)
    emergency_contact: str = Field(..., min_length=5, max_length=100)
    insurance_info: Optional[Dict[str, Any]] = None
    medical_history: Optional[str] = None
    allergies: Optional[List[str]] = None
    medications: Optional[List[str]] = None

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    email: Optional[str] = Field(None, pattern=r"^[^@]+@[^@]+\.[^@]+$")
    address: Optional[str] = Field(None, min_length=10, max_length=200)
    emergency_contact: Optional[str] = Field(None, min_length=5, max_length=100)
    insurance_info: Optional[Dict[str, Any]] = None
    medical_history: Optional[str] = None
    allergies: Optional[List[str]] = None
    medications: Optional[List[str]] = None

class Patient(PatientBase):
    id: str
    user_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ============================================================================
# DOCTOR MODELS
# ============================================================================

class DoctorBase(BaseModel):
    specialization: str = Field(..., min_length=2, max_length=100)
    license_number: str = Field(..., min_length=5, max_length=50)
    years_experience: Optional[int] = Field(None, ge=0, le=50)
    education: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    is_active: bool = True

class DoctorCreate(DoctorBase):
    user_id: Optional[str] = None  # Optional - can create user automatically
    # User creation fields (when user_id is not provided)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class DoctorUpdate(BaseModel):
    specialization: Optional[str] = Field(None, min_length=2, max_length=100)
    years_experience: Optional[int] = Field(None, ge=0, le=50)
    education: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    is_active: Optional[bool] = None

class Doctor(DoctorBase):
    id: str
    user_id: str
    first_name: str
    last_name: str
    full_name: str
    email: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ============================================================================
# APPOINTMENT MODELS
# ============================================================================

class AppointmentBase(BaseModel):
    patient_id: str
    doctor_id: str
    appointment_type: AppointmentType
    scheduled_date: datetime
    duration_minutes: int = Field(30, ge=15, le=480)  # 15 min to 8 hours
    notes: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    patient_id: Optional[str] = None
    doctor_id: Optional[str] = None
    appointment_type: Optional[AppointmentType] = None
    scheduled_date: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=15, le=480)
    notes: Optional[str] = None
    status: Optional[AppointmentStatus] = None

class Appointment(AppointmentBase):
    id: str
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class AppointmentResponse(Appointment):
    """Enhanced appointment response with patient and doctor details"""
    patient_name: str
    patient_email: str
    doctor_name: str
    doctor_specialization: str
    appointment_date: datetime  # Alias for scheduled_date for frontend compatibility
    ai_notes: Optional[str] = None
    risk_assessment: Optional[str] = None
    follow_up_recommendations: Optional[str] = None

# ============================================================================
# OFFICE VISIT MODELS
# ============================================================================

class OfficeVisitBase(BaseModel):
    patient_id: str
    doctor_id: str
    visit_type: VisitType
    chief_complaint: str = Field(..., min_length=10, max_length=500)
    vital_signs: Optional[Dict[str, Any]] = None
    examination_notes: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment_plan: Optional[str] = None
    prescriptions: Optional[List[str]] = None
    follow_up_date: Optional[datetime] = None

class OfficeVisitCreate(OfficeVisitBase):
    appointment_id: Optional[str] = None
    nurse_id: Optional[str] = None

class OfficeVisitUpdate(BaseModel):
    chief_complaint: Optional[str] = Field(None, min_length=10, max_length=500)
    vital_signs: Optional[Dict[str, Any]] = None
    examination_notes: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment_plan: Optional[str] = None
    prescriptions: Optional[List[str]] = None
    follow_up_date: Optional[datetime] = None

class OfficeVisit(OfficeVisitBase):
    id: str
    appointment_id: Optional[str] = None
    nurse_id: Optional[str] = None
    visit_date: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ============================================================================
# MEDICAL RECORD MODELS
# ============================================================================

class MedicalRecordBase(BaseModel):
    patient_id: str
    record_type: str = Field(..., min_length=2, max_length=50)
    content: str = Field(..., min_length=10, max_length=2000)
    metadata: Optional[Dict[str, Any]] = None

class MedicalRecordCreate(MedicalRecordBase):
    office_visit_id: Optional[str] = None

class MedicalRecordUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=10, max_length=2000)
    metadata: Optional[Dict[str, Any]] = None

class MedicalRecord(MedicalRecordBase):
    id: str
    office_visit_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ============================================================================
# SCHEDULE MODELS
# ============================================================================

class ScheduleBase(BaseModel):
    doctor_id: str
    date: datetime
    start_time: str = Field(..., pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    end_time: str = Field(..., pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    is_available: bool = True
    notes: Optional[str] = None

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleUpdate(BaseModel):
    start_time: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    end_time: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    is_available: Optional[bool] = None
    notes: Optional[str] = None

class Schedule(ScheduleBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ============================================================================
# LLM INTERACTION MODELS
# ============================================================================

class LLMInteractionBase(BaseModel):
    interaction_type: str = Field(..., min_length=2, max_length=50)
    user_input: str = Field(..., min_length=1, max_length=2000)
    llm_response: str = Field(..., min_length=1, max_length=5000)
    context: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)

class LLMInteractionCreate(LLMInteractionBase):
    patient_id: Optional[str] = None
    doctor_id: Optional[str] = None

class LLMInteraction(LLMInteractionBase):
    id: str
    patient_id: Optional[str] = None
    doctor_id: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============================================================================
# KNOWLEDGE BASE MODELS
# ============================================================================

class KnowledgeBaseBase(BaseModel):
    category: str = Field(..., min_length=2, max_length=100)
    title: str = Field(..., min_length=5, max_length=200)
    content: str = Field(..., min_length=10, max_length=10000)
    source: Optional[str] = Field(None, max_length=200)
    version: Optional[str] = Field(None, max_length=20)
    is_active: bool = True

class KnowledgeBaseCreate(KnowledgeBaseBase):
    pass

class KnowledgeBaseUpdate(BaseModel):
    category: Optional[str] = Field(None, min_length=2, max_length=100)
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    content: Optional[str] = Field(None, min_length=10, max_length=10000)
    source: Optional[str] = Field(None, max_length=200)
    version: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None

class KnowledgeBase(KnowledgeBaseBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ============================================================================
# PATIENT EDUCATION MODELS
# ============================================================================

class PatientEducationBase(BaseModel):
    patient_id: str
    topic: str = Field(..., min_length=5, max_length=200)
    content: str = Field(..., min_length=10, max_length=5000)
    difficulty_level: str = Field(..., pattern=r"^(basic|intermediate|advanced)$")
    language: str = Field("en", min_length=2, max_length=10)
    is_read: bool = False

class PatientEducationCreate(PatientEducationBase):
    pass

class PatientEducationUpdate(BaseModel):
    topic: Optional[str] = Field(None, min_length=5, max_length=200)
    content: Optional[str] = Field(None, min_length=10, max_length=5000)
    difficulty_level: Optional[str] = Field(None, pattern=r"^(basic|intermediate|advanced)$")
    language: Optional[str] = Field(None, min_length=2, max_length=10)
    is_read: Optional[bool] = None

class PatientEducation(PatientEducationBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============================================================================
# AI SERVICE MODELS
# ============================================================================

class PatientNoteInput(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    note: str = Field(..., min_length=10, max_length=5000, description="Patient medical note")

class AIProcessingResult(BaseModel):
    session_id: str
    success: bool
    workflow_type: str
    patient_report: Optional[Dict[str, Any]] = None
    risk_assessment: Optional[Dict[str, Any]] = None
    treatment_recommendations: Optional[Dict[str, Any]] = None
    processing_time: float
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# ============================================================================
# RESPONSE MODELS
# ============================================================================

class HealthCheck(BaseModel):
    status: str
    service: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
