"""
Clinic service routers with PostgreSQL integration
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime, timedelta
import uuid
import sys
import os

# Add project root to path to import shared models and database
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from shared.models import (
    Patient, PatientCreate, PatientUpdate,
    Appointment, AppointmentCreate, AppointmentUpdate, AppointmentResponse,
    OfficeVisit, OfficeVisitCreate, OfficeVisitUpdate,
    Doctor, DoctorCreate, DoctorUpdate,
    Schedule, ScheduleCreate, ScheduleUpdate,
    AppointmentStatus, AppointmentType, VisitType
)
from database.connection import get_db_session
from database.models.patient import Patient as DBPatient
from database.models.doctor import Doctor as DBDoctor
from database.models.appointment import Appointment as DBAppointment
from database.models.office_visit import OfficeVisit as DBOfficeVisit
from database.models.schedule import Schedule as DBSchedule
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_, Date

router = APIRouter(prefix="/clinic", tags=["clinic"])

# Helper functions
def get_patient_by_id(db: Session, patient_id: str) -> Optional[DBPatient]:
    """Get patient by ID from database"""
    stmt = select(DBPatient).where(DBPatient.id == patient_id)
    result = db.execute(stmt)
    return result.scalar_one_or_none()

def get_doctor_by_id(db: Session, doctor_id: str) -> Optional[DBDoctor]:
    """Get doctor by ID from database"""
    stmt = select(DBDoctor).where(DBDoctor.id == doctor_id)
    result = db.execute(stmt)
    return result.scalar_one_or_none()

def get_appointment_by_id(db: Session, appointment_id: str) -> Optional[DBAppointment]:
    """Get appointment by ID from database"""
    stmt = select(DBAppointment).where(DBAppointment.id == appointment_id)
    result = db.execute(stmt)
    return result.scalar_one_or_none()

def get_user_by_id(db: Session, user_id: str):
    """Get user by ID from database"""
    from database.models.user import User as DBUser
    stmt = select(DBUser).where(DBUser.id == user_id)
    result = db.execute(stmt)
    return result.scalar_one_or_none()

# Patient routes
@router.post("/patients", response_model=Patient)
async def create_patient(patient_data: PatientCreate):
    """Create a new patient"""
    with get_db_session() as db:
        patient_id = uuid.uuid4()
        patient = DBPatient(
            id=patient_id,
            first_name=patient_data.first_name,
            last_name=patient_data.last_name,
            date_of_birth=patient_data.date_of_birth,
            gender=patient_data.gender,
            phone=patient_data.phone,
            email=patient_data.email,
            address=patient_data.address,
            emergency_contact=patient_data.emergency_contact,
            insurance_info=patient_data.insurance_info,
            medical_history=patient_data.medical_history,
            allergies=patient_data.allergies,
            medications=patient_data.medications,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(patient)
        db.commit()
        db.refresh(patient)
        
        return {
            "id": str(patient.id),
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "date_of_birth": patient.date_of_birth,
            "gender": patient.gender,
            "phone": patient.phone,
            "email": patient.email,
            "address": patient.address,
            "emergency_contact": patient.emergency_contact,
            "insurance_info": patient.insurance_info,
            "medical_history": patient.medical_history,
            "allergies": patient.allergies,
            "medications": patient.medications,
            "created_at": patient.created_at,
            "updated_at": patient.updated_at
        }

@router.get("/patients", response_model=List[Patient])
async def get_patients(skip: int = 0, limit: int = 100):
    """Get all patients with pagination"""
    with get_db_session() as db:
        stmt = select(DBPatient).offset(skip).limit(limit)
        result = db.execute(stmt)
        patients = result.scalars().all()
        
        return [
            {
                "id": str(patient.id),
                "first_name": patient.first_name,
                "last_name": patient.last_name,
                "date_of_birth": patient.date_of_birth,
                "gender": patient.gender,
                "phone": patient.phone,
                "email": patient.email,
                "address": patient.address,
                "emergency_contact": patient.emergency_contact,
                "insurance_info": patient.insurance_info,
                "medical_history": patient.medical_history,
                "allergies": patient.allergies,
                "medications": patient.medications,
                "created_at": patient.created_at,
                "updated_at": patient.updated_at
            }
            for patient in patients
        ]

@router.get("/patients/{patient_id}", response_model=Patient)
async def get_patient(patient_id: str):
    """Get a specific patient by ID"""
    with get_db_session() as db:
        patient = get_patient_by_id(db, patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        return {
            "id": str(patient.id),
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "date_of_birth": patient.date_of_birth,
            "gender": patient.gender,
            "phone": patient.phone,
            "email": patient.email,
            "address": patient.address,
            "emergency_contact": patient.emergency_contact,
            "insurance_info": patient.insurance_info,
            "medical_history": patient.medical_history,
            "allergies": patient.allergies,
            "medications": patient.medications,
            "created_at": patient.created_at,
            "updated_at": patient.updated_at
        }

@router.put("/patients/{patient_id}", response_model=Patient)
async def update_patient(patient_id: str, patient_data: PatientUpdate):
    """Update a patient"""
    with get_db_session() as db:
        patient = get_patient_by_id(db, patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Update only provided fields
        update_data = patient_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(patient, field, value)
        
        patient.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(patient)
        
        return {
            "id": str(patient.id),
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "date_of_birth": patient.date_of_birth,
            "gender": patient.gender,
            "phone": patient.phone,
            "email": patient.email,
            "address": patient.address,
            "emergency_contact": patient.emergency_contact,
            "insurance_info": patient.insurance_info,
            "medical_history": patient.medical_history,
            "allergies": patient.allergies,
            "medications": patient.medications,
            "created_at": patient.created_at,
            "updated_at": patient.updated_at
        }

@router.delete("/patients/{patient_id}")
async def delete_patient(patient_id: str):
    """Delete a patient"""
    with get_db_session() as db:
        patient = get_patient_by_id(db, patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        db.delete(patient)
        db.commit()
        return {"message": "Patient deleted successfully"}

# Doctor routes
@router.post("/doctors", response_model=Doctor)
async def create_doctor(doctor_data: DoctorCreate):
    """Create a new doctor"""
    with get_db_session() as db:
        # Import User model here to avoid circular imports
        from database.models.user import User as DBUser
        
        # If user_id is not provided, create a new user first
        if not doctor_data.user_id:
            if not all([doctor_data.first_name, doctor_data.last_name, doctor_data.email]):
                raise HTTPException(
                    status_code=400, 
                    detail="When user_id is not provided, first_name, last_name, and email are required"
                )
            
            # Create new user
            user_id = uuid.uuid4()
            new_user = DBUser(
                id=user_id,
                username=doctor_data.email,  # Use email as username
                email=doctor_data.email,
                first_name=doctor_data.first_name,
                last_name=doctor_data.last_name,
                full_name=f"{doctor_data.first_name} {doctor_data.last_name}",
                password_hash="temporary_hash",  # Will be updated on first login
                role="doctor",
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(new_user)
            db.flush()  # Get the user ID without committing
            
            # Use the new user's ID
            doctor_data.user_id = str(user_id)
        
        doctor_id = uuid.uuid4()
        doctor = DBDoctor(
            id=doctor_id,
            user_id=doctor_data.user_id,
            specialization=doctor_data.specialization,
            license_number=doctor_data.license_number,
            years_experience=doctor_data.years_experience,
            education=doctor_data.education,
            certifications=doctor_data.certifications,
            is_active=doctor_data.is_active,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(doctor)
        db.commit()
        db.refresh(doctor)
        
        # Get user information for enhanced response
        user = get_user_by_id(db, str(doctor.user_id))
        
        return {
            "id": str(doctor.id),
            "user_id": str(doctor.user_id),
            "first_name": user.first_name if user else "",
            "last_name": user.last_name if user else "",
            "full_name": user.full_name if user else "",
            "email": user.email if user else "",
            "specialization": doctor.specialization,
            "license_number": doctor.license_number,
            "years_experience": doctor.years_experience,
            "education": doctor.education,
            "certifications": doctor.certifications,
            "is_active": doctor.is_active,
            "created_at": doctor.created_at,
            "updated_at": doctor.updated_at
        }

@router.get("/doctors", response_model=List[Doctor])
async def get_doctors(skip: int = 0, limit: int = 100):
    """Get all doctors with pagination"""
    with get_db_session() as db:
        # Import User model here to avoid circular imports
        from database.models.user import User as DBUser
        
        # Join with User model to get required fields
        stmt = select(DBDoctor, DBUser).join(
            DBUser, DBDoctor.user_id == DBUser.id
        ).offset(skip).limit(limit)
        
        result = db.execute(stmt)
        rows = result.all()
        
        return [
            {
                "id": str(doctor.id),
                "user_id": str(doctor.user_id),
                "first_name": user.first_name if user else "",
                "last_name": user.last_name if user else "",
                "full_name": user.full_name,
                "email": user.email,
                "specialization": doctor.specialization,
                "license_number": doctor.license_number,
                "years_experience": doctor.years_experience,
                "education": doctor.education,
                "certifications": doctor.certifications,
                "is_active": doctor.is_active,
                "created_at": doctor.created_at,
                "updated_at": doctor.updated_at
            }
            for doctor, user in rows
        ]

@router.get("/doctors/{doctor_id}", response_model=Doctor)
async def get_doctor(doctor_id: str):
    """Get a specific doctor by ID"""
    with get_db_session() as db:
        # Import User model here to avoid circular imports
        from database.models.user import User as DBUser
        
        # Join with User model to get required fields
        stmt = select(DBDoctor, DBUser).join(
            DBUser, DBDoctor.user_id == DBUser.id
        ).where(DBDoctor.id == doctor_id)
        
        result = db.execute(stmt)
        row = result.first()
        
        if not row:
            raise HTTPException(status_code=404, detail="Doctor not found")
        
        doctor, user = row
        
        return {
            "id": str(doctor.id),
            "user_id": str(doctor.user_id),
            "first_name": user.first_name if user else "",
            "last_name": user.last_name if user else "",
            "full_name": user.full_name,
            "email": user.email,
            "specialization": doctor.specialization,
            "license_number": doctor.license_number,
            "years_experience": doctor.years_experience,
            "education": doctor.education,
            "certifications": doctor.certifications,
            "is_active": doctor.is_active,
            "created_at": doctor.created_at,
            "updated_at": doctor.updated_at
        }

@router.put("/doctors/{doctor_id}", response_model=Doctor)
async def update_doctor(doctor_id: str, doctor_data: DoctorUpdate):
    """Update a doctor"""
    with get_db_session() as db:
        doctor = get_doctor_by_id(db, doctor_id)
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")
        
        # Update only provided fields
        update_data = doctor_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(doctor, field, value)
        
        doctor.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(doctor)
        
        # Get user information for enhanced response
        user = get_user_by_id(db, str(doctor.user_id))
        
        return {
            "id": str(doctor.id),
            "user_id": str(doctor.user_id),
            "first_name": user.first_name if user else "",
            "last_name": user.last_name if user else "",
            "full_name": user.full_name if user else "",
            "email": user.email if user else "",
            "specialization": doctor.specialization,
            "license_number": doctor.license_number,
            "years_experience": doctor.years_experience,
            "education": doctor.education,
            "certifications": doctor.certifications,
            "is_active": doctor.is_active,
            "created_at": doctor.created_at,
            "updated_at": doctor.updated_at
        }

@router.delete("/doctors/{doctor_id}")
async def delete_doctor(doctor_id: str):
    """Delete a doctor"""
    with get_db_session() as db:
        doctor = get_doctor_by_id(db, doctor_id)
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")
        
        db.delete(doctor)
        db.commit()
        return {"message": "Doctor deleted successfully"}

# Appointment routes
@router.post("/appointments", response_model=Appointment)
async def create_appointment(appointment_data: AppointmentCreate):
    """Create a new appointment"""
    with get_db_session() as db:
        appointment_id = uuid.uuid4()
        appointment = DBAppointment(
            id=appointment_id,
            patient_id=appointment_data.patient_id,
            doctor_id=appointment_data.doctor_id,
            appointment_type=appointment_data.appointment_type,
            scheduled_date=appointment_data.scheduled_date,
            duration_minutes=appointment_data.duration_minutes,
            notes=appointment_data.notes,
            status=AppointmentStatus.SCHEDULED,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(appointment)
        db.commit()
        db.refresh(appointment)
        
        # Get patient and doctor information for enhanced response
        patient = get_patient_by_id(db, str(appointment.patient_id))
        doctor = get_doctor_by_id(db, str(appointment.doctor_id))
        
        return {
            "id": str(appointment.id),
            "patient_id": str(appointment.patient_id),
            "doctor_id": str(appointment.doctor_id),
            "patient_name": f"{patient.first_name} {patient.last_name}" if patient else "Unknown",
            "patient_email": patient.email if patient else None,
            "doctor_name": f"Dr. {doctor.specialization}" if doctor else "Unknown",
            "doctor_specialization": doctor.specialization if doctor else None,
            "appointment_type": appointment.appointment_type,
            "status": appointment.status,
            "scheduled_date": appointment.scheduled_date,
            "appointment_date": appointment.scheduled_date,  # Alias for frontend compatibility
            "duration_minutes": appointment.duration_minutes,
            "notes": appointment.notes,
            "ai_notes": appointment.ai_notes,
            "risk_assessment": appointment.risk_assessment,
            "follow_up_recommendations": appointment.follow_up_recommendations,
            "created_at": appointment.created_at,
            "updated_at": appointment.updated_at
        }

@router.get("/appointments", response_model=List[AppointmentResponse])
async def get_appointments(
    search: str = "",
    status: str = "all",
    date: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """Get appointments with filters and enhanced data"""
    with get_db_session() as db:
        # Build query with joins to get patient and doctor information
        stmt = select(DBAppointment, DBPatient, DBDoctor).join(
            DBPatient, DBAppointment.patient_id == DBPatient.id
        ).join(
            DBDoctor, DBAppointment.doctor_id == DBDoctor.id
        )
        
        # Apply filters
        if search:
            stmt = stmt.where(
                or_(
                    DBPatient.first_name.ilike(f"%{search}%"),
                    DBPatient.last_name.ilike(f"%{search}%"),
                    DBDoctor.specialization.ilike(f"%{search}%")
                )
            )
        
        if status != "all":
            stmt = stmt.where(DBAppointment.status == status)
        
        if date:
            stmt = stmt.where(DBAppointment.scheduled_date.cast(Date) == date)
        
        # Apply pagination
        stmt = stmt.offset(offset).limit(limit)
        
        result = db.execute(stmt)
        rows = result.all()
        
        return [
            {
                "id": str(appointment.id),
                "patient_id": str(appointment.patient_id),
                "doctor_id": str(appointment.doctor_id),
                "patient_name": f"{patient.first_name} {patient.last_name}",
                "patient_email": patient.email,
                "doctor_name": f"Dr. {doctor.specialization}",  # Will be improved with user join
                "doctor_specialization": doctor.specialization,
                "appointment_type": appointment.appointment_type,
                "status": appointment.status,
                "scheduled_date": appointment.scheduled_date,
                "appointment_date": appointment.scheduled_date,  # Alias for frontend compatibility
                "duration_minutes": appointment.duration_minutes,
                "notes": appointment.notes,
                "ai_notes": appointment.ai_notes,
                "risk_assessment": appointment.risk_assessment,
                "follow_up_recommendations": appointment.follow_up_recommendations,
                "created_at": appointment.created_at,
                "updated_at": appointment.updated_at
            }
            for appointment, patient, doctor in rows
        ]

@router.get("/appointments/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(appointment_id: str):
    """Get a specific appointment by ID with enhanced data"""
    with get_db_session() as db:
        # Get appointment with patient and doctor information
        stmt = select(DBAppointment, DBPatient, DBDoctor).join(
            DBPatient, DBAppointment.patient_id == DBPatient.id
        ).join(
            DBDoctor, DBAppointment.doctor_id == DBDoctor.id
        ).where(DBAppointment.id == appointment_id)
        
        result = db.execute(stmt)
        row = result.first()
        
        if not row:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        appointment, patient, doctor = row
        
        return {
            "id": str(appointment.id),
            "patient_id": str(appointment.patient_id),
            "doctor_id": str(appointment.doctor_id),
            "patient_name": f"{patient.first_name} {patient.last_name}",
            "patient_email": patient.email,
            "doctor_name": f"Dr. {doctor.specialization}",  # Temporary, need to get user info
            "doctor_specialization": doctor.specialization,
            "appointment_type": appointment.appointment_type,
            "status": appointment.status,
            "scheduled_date": appointment.scheduled_date,
            "appointment_date": appointment.scheduled_date,  # Alias for frontend compatibility
            "duration_minutes": appointment.duration_minutes,
            "notes": appointment.notes,
            "ai_notes": appointment.ai_notes,
            "risk_assessment": appointment.risk_assessment,
            "follow_up_recommendations": appointment.follow_up_recommendations,
            "created_at": appointment.created_at,
            "updated_at": appointment.updated_at
        }

@router.put("/appointments/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(appointment_id: str, appointment_data: AppointmentUpdate):
    """Update an appointment"""
    with get_db_session() as db:
        appointment = get_appointment_by_id(db, appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        # Update only provided fields
        update_data = appointment_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(appointment, field, value)
        
        appointment.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(appointment)
        
        # Get patient and doctor information for enhanced response
        # Use the updated patient_id and doctor_id if they were changed
        patient = get_patient_by_id(db, str(appointment.patient_id))
        doctor = get_doctor_by_id(db, str(appointment.doctor_id))
        
        return {
            "id": str(appointment.id),
            "patient_id": str(appointment.patient_id),
            "doctor_id": str(appointment.doctor_id),
            "patient_name": f"{patient.first_name} {patient.last_name}" if patient else "Unknown",
            "patient_email": patient.email if patient else None,
            "doctor_name": f"Dr. {doctor.specialization}" if doctor else "Unknown",
            "doctor_specialization": doctor.specialization if doctor else None,
            "appointment_type": appointment.appointment_type,
            "status": appointment.status,
            "scheduled_date": appointment.scheduled_date,
            "appointment_date": appointment.scheduled_date,  # Alias for frontend compatibility
            "duration_minutes": appointment.duration_minutes,
            "notes": appointment.notes,
            "ai_notes": appointment.ai_notes,
            "risk_assessment": appointment.risk_assessment,
            "follow_up_recommendations": appointment.follow_up_recommendations,
            "created_at": appointment.created_at,
            "updated_at": appointment.updated_at
        }

@router.delete("/appointments/{appointment_id}")
async def delete_appointment(appointment_id: str):
    """Delete an appointment"""
    with get_db_session() as db:
        appointment = get_appointment_by_id(db, appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        db.delete(appointment)
        db.commit()
        return {"message": "Appointment deleted successfully"}

# Dashboard endpoints
@router.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    with get_db_session() as db:
        # Get counts using SQLAlchemy
        total_patients = db.query(DBPatient).count()
        total_doctors = db.query(DBDoctor).filter(DBDoctor.is_active == True).count()
        total_appointments = db.query(DBAppointment).count()
        
        # Get today's appointments
        today = datetime.now().date()
        today_appointments = db.query(DBAppointment).filter(
            DBAppointment.scheduled_date.cast(Date) == today
        ).count()
        
        return {
            "total_patients": total_patients,
            "total_doctors": total_doctors,
            "total_appointments": total_appointments,
            "today_appointments": today_appointments
        }

@router.get("/dashboard/recent-appointments")
async def get_recent_appointments(limit: int = 5):
    """Get recent appointments"""
    with get_db_session() as db:
        # Get recent appointments with patient and doctor info
        stmt = select(DBAppointment, DBPatient, DBDoctor).join(
            DBPatient, DBAppointment.patient_id == DBPatient.id
        ).join(
            DBDoctor, DBAppointment.doctor_id == DBDoctor.id
        ).order_by(DBAppointment.created_at.desc()).limit(limit)
        
        result = db.execute(stmt)
        rows = result.all()
        
        return [
            {
                "id": str(appointment.id),
                "patient_name": f"{patient.first_name} {patient.last_name}",
                "patient_email": patient.email,
                "doctor_name": f"Dr. {doctor.specialization}",
                "doctor_specialization": doctor.specialization,
                "appointment_type": appointment.appointment_type,
                "status": appointment.status,
                "scheduled_date": appointment.scheduled_date,
                "appointment_date": appointment.scheduled_date,  # Alias for frontend compatibility
                "created_at": appointment.created_at
            }
            for appointment, patient, doctor in rows
        ]

@router.get("/dashboard/recent-appointments")
async def get_recent_appointments(limit: int = 5):
    """Get recent appointments for dashboard"""
    with get_db_session() as db:
        # Get recent appointments with patient and doctor info
        stmt = select(DBAppointment, DBPatient, DBDoctor).join(
            DBPatient, DBAppointment.patient_id == DBPatient.id
        ).join(
            DBDoctor, DBAppointment.doctor_id == DBDoctor.id
        ).order_by(DBAppointment.created_at.desc()).limit(limit)

        result = db.execute(stmt)
        rows = result.all()

        return [
            {
                "id": str(appointment.id),
                "patient_name": f"{patient.first_name} {patient.last_name}",
                "patient_email": patient.email,
                "doctor_name": f"Dr. {doctor.specialization}",
                "doctor_specialization": doctor.specialization,
                "appointment_type": appointment.appointment_type,
                "status": appointment.status,
                "scheduled_date": appointment.scheduled_date,
                "appointment_date": appointment.scheduled_date,  # Alias for frontend compatibility
                "created_at": appointment.created_at
            }
            for appointment, patient, doctor in rows
        ]

@router.get("/dashboard/upcoming-appointments")
async def get_upcoming_appointments(limit: int = 5):
    """Get upcoming appointments for dashboard"""
    with get_db_session() as db:
        # Get upcoming appointments with patient and doctor info
        stmt = select(DBAppointment, DBPatient, DBDoctor).join(
            DBPatient, DBAppointment.patient_id == DBPatient.id
        ).join(
            DBDoctor, DBAppointment.doctor_id == DBDoctor.id
        ).where(
            DBAppointment.scheduled_date >= datetime.now()
        ).order_by(DBAppointment.scheduled_date.asc()).limit(limit)

        result = db.execute(stmt)
        rows = result.all()

        return [
            {
                "id": str(appointment.id),
                "patient_name": f"{patient.first_name} {patient.last_name}",
                "patient_email": patient.email,
                "doctor_name": f"Dr. {doctor.specialization}",
                "doctor_specialization": doctor.specialization,
                "appointment_type": appointment.appointment_type,
                "status": appointment.status,
                "scheduled_date": appointment.scheduled_date,
                "appointment_date": appointment.scheduled_date,  # Alias for frontend compatibility
                "created_at": appointment.created_at
            }
            for appointment, patient, doctor in rows
        ]

@router.get("/appointments/upcoming")
async def get_upcoming_appointments_general(limit: int = 10):
    """Get upcoming appointments (general endpoint)"""
    with get_db_session() as db:
        stmt = select(DBAppointment, DBPatient, DBDoctor).join(
            DBPatient, DBAppointment.patient_id == DBPatient.id
        ).join(
            DBDoctor, DBAppointment.doctor_id == DBDoctor.id
        ).where(
            DBAppointment.scheduled_date >= datetime.now()
        ).order_by(DBAppointment.scheduled_date.asc()).limit(limit)

        result = db.execute(stmt)
        rows = result.all()

        return [
            {
                "id": str(appointment.id),
                "patient_id": str(appointment.patient_id),
                "doctor_id": str(appointment.doctor_id),
                "patient_name": f"{patient.first_name} {patient.last_name}",
                "patient_email": patient.email,
                "doctor_name": f"Dr. {doctor.specialization}",
                "doctor_specialization": doctor.specialization,
                "appointment_type": appointment.appointment_type,
                "status": appointment.status,
                "scheduled_date": appointment.scheduled_date,
                "appointment_date": appointment.scheduled_date,  # Alias for frontend compatibility
                "duration_minutes": appointment.duration_minutes,
                "notes": appointment.notes,
                "created_at": appointment.created_at
            }
            for appointment, patient, doctor in rows
        ]

@router.get("/appointments/today")
async def get_today_appointments():
    """Get today's appointments"""
    with get_db_session() as db:
        today = datetime.now().date()

        stmt = select(DBAppointment, DBPatient, DBDoctor).join(
            DBPatient, DBAppointment.patient_id == DBPatient.id
        ).join(
            DBDoctor, DBAppointment.doctor_id == DBDoctor.id
        ).where(
            DBAppointment.scheduled_date.cast(Date) == today
        ).order_by(DBAppointment.scheduled_date.asc())

        result = db.execute(stmt)
        rows = result.all()

        return [
            {
                "id": str(appointment.id),
                "patient_id": str(appointment.patient_id),
                "doctor_id": str(appointment.doctor_id),
                "patient_name": f"{patient.first_name} {patient.last_name}",
                "patient_email": patient.email,
                "doctor_name": f"Dr. {doctor.specialization}",
                "doctor_specialization": doctor.specialization,
                "appointment_type": appointment.appointment_type,
                "status": appointment.status,
                "scheduled_date": appointment.scheduled_date,
                "appointment_date": appointment.scheduled_date,  # Alias for frontend compatibility
                "duration_minutes": appointment.duration_minutes,
                "notes": appointment.notes,
                "created_at": appointment.created_at
            }
            for appointment, patient, doctor in rows
        ]

# Search endpoints
@router.get("/patients/search")
async def search_patients(q: str, skip: int = 0, limit: int = 50):
    """Search patients by name, email, or phone"""
    with get_db_session() as db:
        if not q or len(q.strip()) < 2:
            raise HTTPException(status_code=400, detail="Search query must be at least 2 characters")

        search_term = f"%{q.strip()}%"

        stmt = select(DBPatient).where(
            or_(
                DBPatient.first_name.ilike(search_term),
                DBPatient.last_name.ilike(search_term),
                DBPatient.email.ilike(search_term),
                DBPatient.phone.ilike(search_term)
            )
        ).offset(skip).limit(limit)

        result = db.execute(stmt)
        patients = result.scalars().all()

        return [
            {
                "id": str(patient.id),
                "first_name": patient.first_name,
                "last_name": patient.last_name,
                "email": patient.email,
                "phone": patient.phone,
                "date_of_birth": patient.date_of_birth,
                "gender": patient.gender,
                "address": patient.address,
                "emergency_contact": patient.emergency_contact,
                "created_at": patient.created_at,
                "updated_at": patient.updated_at
            }
            for patient in patients
        ]

@router.get("/doctors/search")
async def search_doctors(q: str, skip: int = 0, limit: int = 50):
    """Search doctors by name, specialization, or license"""
    with get_db_session() as db:
        if not q or len(q.strip()) < 2:
            raise HTTPException(status_code=400, detail="Search query must be at least 2 characters")

        search_term = f"%{q.strip()}%"

        # Join with User model to search by name
        from database.models.user import User as DBUser

        stmt = select(DBDoctor, DBUser).join(
            DBUser, DBDoctor.user_id == DBUser.id
        ).where(
            or_(
                DBUser.first_name.ilike(search_term),
                DBUser.last_name.ilike(search_term),
                DBUser.full_name.ilike(search_term),
                DBDoctor.specialization.ilike(search_term),
                DBDoctor.license_number.ilike(search_term)
            )
        ).offset(skip).limit(limit)

        result = db.execute(stmt)
        rows = result.all()

        return [
            {
                "id": str(doctor.id),
                "user_id": str(doctor.user_id),
                "first_name": user.first_name if user else "",
                "last_name": user.last_name if user else "",
                "full_name": user.full_name if user else "",
                "email": user.email if user else "",
                "specialization": doctor.specialization,
                "license_number": doctor.license_number,
                "years_experience": doctor.years_experience,
                "education": doctor.education,
                "certifications": doctor.certifications,
                "is_active": doctor.is_active,
                "created_at": doctor.created_at,
                "updated_at": doctor.updated_at
            }
            for doctor, user in rows
        ]

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "LotusHealth Clinic Service"}
