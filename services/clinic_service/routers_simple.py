"""
Simple Clinic service routers with PostgreSQL integration
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime, timedelta
import uuid
import sys
import os
import json

# Add project root to path to import shared models
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from shared.models import (
    Patient, PatientCreate, PatientUpdate,
    Appointment, AppointmentCreate, AppointmentUpdate,
    OfficeVisit, OfficeVisitCreate, OfficeVisitUpdate,
    Doctor, DoctorCreate, DoctorUpdate,
    Schedule, ScheduleCreate, ScheduleUpdate,
    AppointmentStatus, AppointmentType, VisitType
)

# Simple database connection without complex models
import psycopg2
from psycopg2.extras import RealDictCursor

router = APIRouter(prefix="/clinic", tags=["clinic"])

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'postgres'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'lotushealth'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'password')
    )

# Patient endpoints
@router.post("/patients", response_model=Patient)
async def create_patient(patient_data: PatientCreate):
    """Create a new patient"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Generate new patient ID
        patient_id = str(uuid.uuid4())
        
        # Insert patient
        cursor.execute("""
            INSERT INTO patients (
                id, first_name, last_name, date_of_birth, gender, 
                phone, email, address, emergency_contact, 
                insurance_info, medical_history, allergies, medications
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (
            patient_id,
            patient_data.first_name,
            patient_data.last_name,
            patient_data.date_of_birth,
            patient_data.gender,
            patient_data.phone,
            patient_data.email,
            patient_data.address,
            patient_data.emergency_contact,
            json.dumps(patient_data.insurance_info) if patient_data.insurance_info else None,
            patient_data.medical_history,
            patient_data.allergies,
            patient_data.medications
        ))
        
        patient = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "id": str(patient['id']),
            "first_name": patient['first_name'],
            "last_name": patient['last_name'],
            "date_of_birth": patient['date_of_birth'],
            "gender": patient['gender'],
            "phone": patient['phone'],
            "email": patient['email'],
            "address": patient['address'],
            "emergency_contact": patient['emergency_contact'],
            "insurance_info": patient['insurance_info'],
            "medical_history": patient['medical_history'],
            "allergies": patient['allergies'],
            "medications": patient['medications'],
            "created_at": patient['created_at'],
            "updated_at": patient['updated_at']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating patient: {str(e)}")

@router.get("/patients", response_model=List[Patient])
async def get_patients(search: str = "", limit: int = 100, offset: int = 0):
    """Get all patients with optional search"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        if search:
            cursor.execute("""
                SELECT * FROM patients 
                WHERE first_name ILIKE %s OR last_name ILIKE %s OR email ILIKE %s
                ORDER BY last_name, first_name
                LIMIT %s OFFSET %s
            """, (f"%{search}%", f"%{search}%", f"%{search}%", limit, offset))
        else:
            cursor.execute("""
                SELECT * FROM patients 
                ORDER BY last_name, first_name
                LIMIT %s OFFSET %s
            """, (limit, offset))
        
        patients = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [
            {
                "id": str(patient['id']),
                "first_name": patient['first_name'],
                "last_name": patient['last_name'],
                "date_of_birth": patient['date_of_birth'],
                "gender": patient['gender'],
                "phone": patient['phone'],
                "email": patient['email'],
                "address": patient['address'],
                "emergency_contact": patient['emergency_contact'],
                "insurance_info": patient['insurance_info'],
                "medical_history": patient['medical_history'],
                "allergies": patient['allergies'],
                "medications": patient['medications'],
                "created_at": patient['created_at'],
                "updated_at": patient['updated_at']
            }
            for patient in patients
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching patients: {str(e)}")

@router.get("/patients/{patient_id}", response_model=Patient)
async def get_patient(patient_id: str):
    """Get patient by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
        patient = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        return {
            "id": str(patient['id']),
            "first_name": patient['first_name'],
            "last_name": patient['last_name'],
            "date_of_birth": patient['date_of_birth'],
            "gender": patient['gender'],
            "phone": patient['phone'],
            "email": patient['email'],
            "address": patient['address'],
            "emergency_contact": patient['emergency_contact'],
            "insurance_info": patient['insurance_info'],
            "medical_history": patient['medical_history'],
            "allergies": patient['allergies'],
            "medications": patient['medications'],
            "created_at": patient['created_at'],
            "updated_at": patient['updated_at']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching patient: {str(e)}")

@router.put("/patients/{patient_id}", response_model=Patient)
async def update_patient(patient_id: str, patient_data: PatientUpdate):
    """Update patient"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Build update query dynamically
        update_fields = []
        values = []
        
        for field, value in patient_data.dict(exclude_unset=True).items():
            update_fields.append(f"{field} = %s")
            # Convert dict to JSON string for JSONB fields
            if field == 'insurance_info' and isinstance(value, dict):
                values.append(json.dumps(value))
            else:
                values.append(value)
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        values.append(patient_id)
        
        cursor.execute(f"""
            UPDATE patients 
            SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING *
        """, values)
        
        patient = cursor.fetchone()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "id": str(patient['id']),
            "first_name": patient['first_name'],
            "last_name": patient['last_name'],
            "date_of_birth": patient['date_of_birth'],
            "gender": patient['gender'],
            "phone": patient['phone'],
            "email": patient['email'],
            "address": patient['address'],
            "emergency_contact": patient['emergency_contact'],
            "insurance_info": patient['insurance_info'],
            "medical_history": patient['medical_history'],
            "allergies": patient['allergies'],
            "medications": patient['medications'],
            "created_at": patient['created_at'],
            "updated_at": patient['updated_at']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating patient: {str(e)}")

@router.delete("/patients/{patient_id}")
async def delete_patient(patient_id: str):
    """Delete patient"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM patients WHERE id = %s", (patient_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"message": "Patient deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting patient: {str(e)}")

# Doctor endpoints
@router.get("/doctors", response_model=List[Doctor])
async def get_doctors():
    """Get all doctors"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT d.*, u.first_name, u.last_name, u.full_name, u.email 
            FROM doctors d
            JOIN users u ON d.user_id = u.id
            WHERE d.is_active = true
            ORDER BY u.full_name
        """)
        
        doctors = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [
            {
                "id": str(doctor['id']),
                "user_id": str(doctor['user_id']),
                "first_name": doctor['first_name'],
                "last_name": doctor['last_name'],
                "full_name": doctor['full_name'],
                "email": doctor['email'],
                "specialization": doctor['specialization'],
                "license_number": doctor['license_number'],
                "years_experience": doctor['years_experience'],
                "education": doctor['education'],
                "certifications": doctor['certifications'],
                "is_active": doctor['is_active'],
                "created_at": doctor['created_at'],
                "updated_at": doctor['updated_at']
            }
            for doctor in doctors
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching doctors: {str(e)}")

@router.get("/doctors/{doctor_id}", response_model=Doctor)
async def get_doctor(doctor_id: str):
    """Get doctor by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT d.*, u.first_name, u.last_name, u.full_name, u.email 
            FROM doctors d
            JOIN users u ON d.user_id = u.id
            WHERE d.id = %s AND d.is_active = true
        """, (doctor_id,))
        
        doctor = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")
        
        return {
            "id": str(doctor['id']),
            "user_id": str(doctor['user_id']),
            "first_name": doctor['first_name'],
            "last_name": doctor['last_name'],
            "full_name": doctor['full_name'],
            "email": doctor['email'],
            "specialization": doctor['specialization'],
            "license_number": doctor['license_number'],
            "years_experience": doctor['years_experience'],
            "education": doctor['education'],
            "certifications": doctor['certifications'],
            "is_active": doctor['is_active'],
            "created_at": doctor['created_at'],
            "updated_at": doctor['updated_at']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching doctor: {str(e)}")

@router.post("/doctors", response_model=Doctor)
async def create_doctor(doctor_data: DoctorCreate):
    """Create a new doctor"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Generate new doctor ID
        doctor_id = str(uuid.uuid4())
        
        # Insert doctor
        cursor.execute("""
            INSERT INTO doctors (
                id, user_id, specialization, license_number, 
                years_experience, education, certifications, is_active
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (
            doctor_id,
            doctor_data.user_id,
            doctor_data.specialization,
            doctor_data.license_number,
            doctor_data.years_experience,
            doctor_data.education,
            doctor_data.certifications,
            doctor_data.is_active if doctor_data.is_active is not None else True
        ))
        
        doctor = cursor.fetchone()
        
        # Get user info
        cursor.execute("SELECT first_name, last_name, full_name, email FROM users WHERE id = %s", (doctor_data.user_id,))
        user = cursor.fetchone()
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "id": str(doctor['id']),
            "user_id": str(doctor['user_id']),
            "first_name": user['first_name'],
            "last_name": user['last_name'],
            "full_name": user['full_name'],
            "email": user['email'],
            "specialization": doctor['specialization'],
            "license_number": doctor['license_number'],
            "years_experience": doctor['years_experience'],
            "education": doctor['education'],
            "certifications": doctor['certifications'],
            "is_active": doctor['is_active'],
            "created_at": doctor['created_at'],
            "updated_at": doctor['updated_at']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating doctor: {str(e)}")

@router.put("/doctors/{doctor_id}", response_model=Doctor)
async def update_doctor(doctor_id: str, doctor_data: DoctorUpdate):
    """Update doctor"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Build update query dynamically
        update_fields = []
        values = []
        
        for field, value in doctor_data.dict(exclude_unset=True).items():
            update_fields.append(f"{field} = %s")
            values.append(value)
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        values.append(doctor_id)
        
        cursor.execute(f"""
            UPDATE doctors 
            SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING *
        """, values)
        
        doctor = cursor.fetchone()
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")
        
        # Get user info
        cursor.execute("SELECT first_name, last_name, full_name, email FROM users WHERE id = %s", (doctor['user_id'],))
        user = cursor.fetchone()
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "id": str(doctor['id']),
            "user_id": str(doctor['user_id']),
            "first_name": user['first_name'],
            "last_name": user['last_name'],
            "full_name": user['full_name'],
            "email": user['email'],
            "specialization": doctor['specialization'],
            "license_number": doctor['license_number'],
            "years_experience": doctor['years_experience'],
            "education": doctor['education'],
            "certifications": doctor['certifications'],
            "is_active": doctor['is_active'],
            "created_at": doctor['created_at'],
            "updated_at": doctor['updated_at']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating doctor: {str(e)}")

@router.delete("/doctors/{doctor_id}")
async def delete_doctor(doctor_id: str):
    """Delete doctor (soft delete by setting is_active to false)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE doctors SET is_active = false, updated_at = CURRENT_TIMESTAMP WHERE id = %s", (doctor_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Doctor not found")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"message": "Doctor deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting doctor: {str(e)}")

# Appointment endpoints
@router.get("/appointments", response_model=List[Appointment])
async def get_appointments(
    search: str = "",
    status: str = "all",
    date: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """Get appointments with filters"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Build query with filters
        where_conditions = []
        params = []
        
        if search:
            where_conditions.append("""
                (p.first_name ILIKE %s OR p.last_name ILIKE %s OR 
                 d.full_name ILIKE %s OR a.notes ILIKE %s)
            """)
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param, search_param])
        
        if status != "all":
            where_conditions.append("a.status = %s")
            params.append(status)
        
        if date:
            where_conditions.append("DATE(a.scheduled_date) = %s")
            params.append(date)
        
        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        cursor.execute(f"""
            SELECT a.*, 
                   p.first_name as patient_first_name, p.last_name as patient_last_name,
                   p.email as patient_email,
                   u.full_name as doctor_name,
                   d.specialization as doctor_specialization
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            JOIN doctors d ON a.doctor_id = d.id
            JOIN users u ON d.user_id = u.id
            {where_clause}
            ORDER BY a.scheduled_date DESC
            LIMIT %s OFFSET %s
        """, params + [limit, offset])
        
        appointments = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [
            {
                "id": str(appointment['id']),
                "patient_id": str(appointment['patient_id']),
                "doctor_id": str(appointment['doctor_id']),
                "patient_name": f"{appointment['patient_first_name']} {appointment['patient_last_name']}",
                "patient_email": appointment['patient_email'],
                "doctor_name": appointment['doctor_name'],
                "doctor_specialization": appointment['doctor_specialization'],
                "appointment_type": appointment['appointment_type'],
                "status": appointment['status'],
                "scheduled_date": appointment['scheduled_date'],
                "appointment_date": appointment['scheduled_date'],  # Alias for frontend compatibility
                "duration_minutes": appointment['duration_minutes'],
                "notes": appointment['notes'],
                "created_at": appointment['created_at'],
                "updated_at": appointment['updated_at']
            }
            for appointment in appointments
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching appointments: {str(e)}")

@router.post("/appointments", response_model=Appointment)
async def create_appointment(appointment_data: AppointmentCreate):
    """Create a new appointment"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Generate new appointment ID
        appointment_id = str(uuid.uuid4())
        
        # Insert appointment
        cursor.execute("""
            INSERT INTO appointments (
                id, patient_id, doctor_id, appointment_type, 
                status, scheduled_date, duration_minutes, notes
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (
            appointment_id,
            appointment_data.patient_id,
            appointment_data.doctor_id,
            appointment_data.appointment_type,
            "scheduled",  # Default status for new appointments
            appointment_data.scheduled_date,
            appointment_data.duration_minutes or 30,
            appointment_data.notes
        ))
        
        appointment = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "id": str(appointment['id']),
            "patient_id": str(appointment['patient_id']),
            "doctor_id": str(appointment['doctor_id']),
            "appointment_type": appointment['appointment_type'],
            "status": appointment['status'],
            "scheduled_date": appointment['scheduled_date'],
            "appointment_date": appointment['scheduled_date'],  # Alias for frontend compatibility
            "duration_minutes": appointment['duration_minutes'],
            "notes": appointment['notes'],
            "created_at": appointment['created_at'],
            "updated_at": appointment['updated_at']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating appointment: {str(e)}")

@router.get("/appointments/{appointment_id}", response_model=Appointment)
async def get_appointment(appointment_id: str):
    """Get a single appointment by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT a.*, 
                   p.first_name as patient_first_name, p.last_name as patient_last_name,
                   p.email as patient_email,
                   u.full_name as doctor_name,
                   d.specialization as doctor_specialization
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            JOIN doctors d ON a.doctor_id = d.id
            JOIN users u ON d.user_id = u.id
            WHERE a.id = %s
        """, (appointment_id,))
        
        appointment = cursor.fetchone()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        cursor.close()
        conn.close()
        
        return {
            "id": str(appointment['id']),
            "patient_id": str(appointment['patient_id']),
            "doctor_id": str(appointment['doctor_id']),
            "patient_name": f"{appointment['patient_first_name']} {appointment['patient_last_name']}",
            "patient_email": appointment['patient_email'],
            "doctor_name": appointment['doctor_name'],
            "doctor_specialization": appointment['doctor_specialization'],
            "appointment_type": appointment['appointment_type'],
            "status": appointment['status'],
            "scheduled_date": appointment['scheduled_date'],
            "appointment_date": appointment['scheduled_date'],  # Alias for frontend compatibility
            "duration_minutes": appointment['duration_minutes'],
            "notes": appointment['notes'],
            "created_at": appointment['created_at'],
            "updated_at": appointment['updated_at']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching appointment: {str(e)}")

@router.put("/appointments/{appointment_id}", response_model=Appointment)
async def update_appointment(appointment_id: str, appointment_data: AppointmentUpdate):
    """Update appointment"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Build update query dynamically
        update_fields = []
        values = []
        
        for field, value in appointment_data.dict(exclude_unset=True).items():
            update_fields.append(f"{field} = %s")
            values.append(value)
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        values.append(appointment_id)
        
        cursor.execute(f"""
            UPDATE appointments 
            SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING *
        """, values)
        
        appointment = cursor.fetchone()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "id": str(appointment['id']),
            "patient_id": str(appointment['patient_id']),
            "doctor_id": str(appointment['doctor_id']),
            "appointment_type": appointment['appointment_type'],
            "status": appointment['status'],
            "scheduled_date": appointment['scheduled_date'],
            "appointment_date": appointment['scheduled_date'],  # Alias for frontend compatibility
            "duration_minutes": appointment['duration_minutes'],
            "notes": appointment['notes'],
            "created_at": appointment['created_at'],
            "updated_at": appointment['updated_at']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating appointment: {str(e)}")

@router.delete("/appointments/{appointment_id}")
async def delete_appointment(appointment_id: str):
    """Delete appointment"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM appointments WHERE id = %s", (appointment_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"message": "Appointment deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting appointment: {str(e)}")

# Dashboard endpoints
@router.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get counts
        cursor.execute("SELECT COUNT(*) as total_patients FROM patients")
        total_patients = cursor.fetchone()['total_patients']
        
        cursor.execute("SELECT COUNT(*) as total_doctors FROM doctors WHERE is_active = true")
        total_doctors = cursor.fetchone()['total_doctors']
        
        cursor.execute("SELECT COUNT(*) as total_appointments FROM appointments")
        total_appointments = cursor.fetchone()['total_appointments']
        
        cursor.execute("SELECT COUNT(*) as today_appointments FROM appointments WHERE DATE(scheduled_date) = CURRENT_DATE")
        today_appointments = cursor.fetchone()['today_appointments']
        
        cursor.close()
        conn.close()
        
        return {
            "total_patients": total_patients,
            "total_doctors": total_doctors,
            "total_appointments": total_appointments,
            "today_appointments": today_appointments
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard stats: {str(e)}")

@router.get("/dashboard/recent-appointments")
async def get_recent_appointments(limit: int = 5):
    """Get recent appointments"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT a.*, 
                   p.first_name as patient_first_name, p.last_name as patient_last_name,
                   p.email as patient_email,
                   u.full_name as doctor_name,
                   d.specialization as doctor_specialization
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            JOIN doctors d ON a.doctor_id = d.id
            JOIN users u ON d.user_id = u.id
            ORDER BY a.created_at DESC
            LIMIT %s
        """, (limit,))
        
        appointments = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [
            {
                "id": str(appointment['id']),
                "patient_name": f"{appointment['patient_first_name']} {appointment['patient_last_name']}",
                "patient_email": appointment['patient_email'],
                "doctor_name": appointment['doctor_name'],
                "doctor_specialization": appointment['doctor_specialization'],
                "appointment_type": appointment['appointment_type'],
                "status": appointment['status'],
                "scheduled_date": appointment['scheduled_date'],
                "appointment_date": appointment['scheduled_date'],  # Alias for frontend compatibility
                "created_at": appointment['created_at']
            }
            for appointment in appointments
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recent appointments: {str(e)}")

@router.get("/dashboard/upcoming-appointments")
async def get_upcoming_appointments(limit: int = 5):
    """Get upcoming appointments"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT a.*, 
                   p.first_name as patient_first_name, p.last_name as patient_last_name,
                   p.email as patient_email,
                   u.full_name as doctor_name,
                   d.specialization as doctor_specialization
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            JOIN doctors d ON a.doctor_id = d.id
            JOIN users u ON d.user_id = u.id
            WHERE a.scheduled_date >= CURRENT_TIMESTAMP
            ORDER BY a.scheduled_date ASC
            LIMIT %s
        """, (limit,))
        
        appointments = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [
            {
                "id": str(appointment['id']),
                "patient_name": f"{appointment['patient_first_name']} {appointment['patient_last_name']}",
                "patient_email": appointment['patient_email'],
                "doctor_name": appointment['doctor_name'],
                "doctor_specialization": appointment['doctor_specialization'],
                "appointment_type": appointment['appointment_type'],
                "status": appointment['status'],
                "scheduled_date": appointment['scheduled_date'],
                "appointment_date": appointment['scheduled_date'],  # Alias for frontend compatibility
                "created_at": appointment['created_at']
            }
            for appointment in appointments
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching upcoming appointments: {str(e)}")

# Schedule routes
@router.post("/schedules", response_model=Schedule)
async def create_schedule(schedule_data: ScheduleCreate):
    """Create a new schedule"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Generate new schedule ID
        schedule_id = str(uuid.uuid4())
        
        # Insert schedule
        cursor.execute("""
            INSERT INTO schedules (
                id, doctor_id, date, start_time, end_time, is_available, notes
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (
            schedule_id,
            schedule_data.doctor_id,
            schedule_data.date,
            schedule_data.start_time,
            schedule_data.end_time,
            schedule_data.is_available,
            schedule_data.notes
        ))
        
        schedule = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "id": str(schedule['id']),
            "doctor_id": str(schedule['doctor_id']),
            "date": schedule['date'],
            "start_time": str(schedule['start_time'])[:5],  # Remove seconds
            "end_time": str(schedule['end_time'])[:5],      # Remove seconds
            "is_available": schedule['is_available'],
            "notes": schedule['notes'],
            "created_at": schedule['created_at'],
            "updated_at": schedule['updated_at']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating schedule: {str(e)}")

@router.get("/schedules", response_model=List[Schedule])
async def get_schedules(doctor_id: Optional[str] = None, date: Optional[datetime] = None):
    """Get schedules with optional filtering"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = "SELECT * FROM schedules WHERE 1=1"
        params = []
        
        if doctor_id:
            query += " AND doctor_id = %s"
            params.append(doctor_id)
        
        if date:
            query += " AND DATE(date) = DATE(%s)"
            params.append(date)
        
        query += " ORDER BY date, start_time"
        
        cursor.execute(query, params)
        schedules = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [
            {
                "id": str(schedule['id']),
                "doctor_id": str(schedule['doctor_id']),
                "date": schedule['date'],
                "start_time": str(schedule['start_time'])[:5],  # Remove seconds
                "end_time": str(schedule['end_time'])[:5],      # Remove seconds
                "is_available": schedule['is_available'],
                "notes": schedule['notes'],
                "created_at": schedule['created_at'],
                "updated_at": schedule['updated_at']
            }
            for schedule in schedules
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching schedules: {str(e)}")

@router.get("/schedules/{schedule_id}", response_model=Schedule)
async def get_schedule(schedule_id: str):
    """Get schedule by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("SELECT * FROM schedules WHERE id = %s", (schedule_id,))
        schedule = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")
        
        return {
            "id": str(schedule['id']),
            "doctor_id": str(schedule['doctor_id']),
            "date": schedule['date'],
            "start_time": str(schedule['start_time'])[:5],  # Remove seconds
            "end_time": str(schedule['end_time'])[:5],      # Remove seconds
            "is_available": schedule['is_available'],
            "notes": schedule['notes'],
            "created_at": schedule['created_at'],
            "updated_at": schedule['updated_at']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching schedule: {str(e)}")

@router.put("/schedules/{schedule_id}", response_model=Schedule)
async def update_schedule(schedule_id: str, schedule_data: ScheduleUpdate):
    """Update schedule"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Build update query dynamically
        update_fields = []
        values = []
        
        for field, value in schedule_data.dict(exclude_unset=True).items():
            update_fields.append(f"{field} = %s")
            values.append(value)
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        values.append(schedule_id)
        
        cursor.execute(f"""
            UPDATE schedules 
            SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING *
        """, values)
        
        schedule = cursor.fetchone()
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "id": str(schedule['id']),
            "doctor_id": str(schedule['doctor_id']),
            "date": schedule['date'],
            "start_time": str(schedule['start_time'])[:5],  # Remove seconds
            "end_time": str(schedule['end_time'])[:5],      # Remove seconds
            "is_available": schedule['is_available'],
            "notes": schedule['notes'],
            "created_at": schedule['created_at'],
            "updated_at": schedule['updated_at']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating schedule: {str(e)}")

@router.delete("/schedules/{schedule_id}")
async def delete_schedule(schedule_id: str):
    """Delete schedule"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM schedules WHERE id = %s", (schedule_id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Schedule not found")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"message": "Schedule deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting schedule: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "LotusHealth Clinic Service"}
