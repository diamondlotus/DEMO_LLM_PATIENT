"""
Clinic service routers
Separate routing logic from main application
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime, timedelta
import uuid
import sys
import os

# Add project root to path to import shared models
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from shared.models import (
    Patient, PatientCreate, PatientUpdate,
    Appointment, AppointmentCreate, AppointmentUpdate,
    OfficeVisit, OfficeVisitCreate, OfficeVisitUpdate,
    Doctor, DoctorCreate, DoctorUpdate,
    Schedule, ScheduleCreate, ScheduleUpdate,
    AppointmentStatus, AppointmentType, VisitType
)

router = APIRouter(prefix="/clinic", tags=["clinic"])

# Mock databases (replace with real database in production)
patients_db = {}
appointments_db = {}
office_visits_db = {}
doctors_db = {}
schedules_db = {}

# Helper functions
def get_patient_by_id(patient_id: str) -> Optional[dict]:
    return patients_db.get(patient_id)

def get_doctor_by_id(doctor_id: str) -> Optional[dict]:
    return doctors_db.get(doctor_id)

def get_appointment_by_id(appointment_id: str) -> Optional[dict]:
    return appointments_db.get(appointment_id)

# Patient routes
@router.post("/patients", response_model=Patient)
async def create_patient(patient_data: PatientCreate):
    patient_id = str(uuid.uuid4())
    patient = {
        "id": patient_id,
        "first_name": patient_data.first_name,
        "last_name": patient_data.last_name,
        "date_of_birth": patient_data.date_of_birth,
        "gender": patient_data.gender,
        "phone": patient_data.phone,
        "email": patient_data.email,
        "address": patient_data.address,
        "emergency_contact": patient_data.emergency_contact,
        "insurance_info": patient_data.insurance_info,
        "medical_history": patient_data.medical_history,
        "allergies": patient_data.allergies,
        "medications": patient_data.medications,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    patients_db[patient_id] = patient
    return patient

@router.get("/patients", response_model=List[Patient])
async def get_patients(skip: int = 0, limit: int = 100):
    patients = list(patients_db.values())
    return patients[skip : skip + limit]

@router.get("/patients/{patient_id}", response_model=Patient)
async def get_patient(patient_id: str):
    patient = get_patient_by_id(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@router.put("/patients/{patient_id}", response_model=Patient)
async def update_patient(patient_id: str, patient_data: PatientUpdate):
    patient = get_patient_by_id(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Update only provided fields
    update_data = patient_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        patient[field] = value
    
    patient["updated_at"] = datetime.now()
    return patient

@router.delete("/patients/{patient_id}")
async def delete_patient(patient_id: str):
    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    del patients_db[patient_id]
    return {"message": "Patient deleted successfully"}

# Doctor routes
@router.post("/doctors", response_model=Doctor)
async def create_doctor(doctor_data: DoctorCreate):
    doctor_id = str(uuid.uuid4())
    doctor = {
        "id": doctor_id,
        "user_id": doctor_data.user_id,
        "specialization": doctor_data.specialization,
        "license_number": doctor_data.license_number,
        "years_experience": doctor_data.years_experience,
        "education": doctor_data.education,
        "certifications": doctor_data.certifications,
        "is_active": doctor_data.is_active,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    doctors_db[doctor_id] = doctor
    return doctor

@router.get("/doctors", response_model=List[Doctor])
async def get_doctors(skip: int = 0, limit: int = 100):
    doctors = list(doctors_db.values())
    return doctors[skip : skip + limit]

@router.get("/doctors/{doctor_id}", response_model=Doctor)
async def get_doctor(doctor_id: str):
    doctor = get_doctor_by_id(doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor

# Appointment routes
@router.post("/appointments", response_model=Appointment)
async def create_appointment(appointment_data: AppointmentCreate):
    appointment_id = str(uuid.uuid4())
    appointment = {
        "id": appointment_id,
        "patient_id": appointment_data.patient_id,
        "doctor_id": appointment_data.doctor_id,
        "appointment_type": appointment_data.appointment_type,
        "status": AppointmentStatus.SCHEDULED,
        "scheduled_date": appointment_data.scheduled_date,
        "duration_minutes": appointment_data.duration_minutes,
        "notes": appointment_data.notes,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    appointments_db[appointment_id] = appointment
    return appointment

@router.get("/appointments", response_model=List[Appointment])
async def get_appointments(skip: int = 0, limit: int = 100):
    appointments = list(appointments_db.values())
    return appointments[skip : skip + limit]

@router.get("/appointments/{appointment_id}", response_model=Appointment)
async def get_appointment(appointment_id: str):
    appointment = get_appointment_by_id(appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment

@router.put("/appointments/{appointment_id}", response_model=Appointment)
async def update_appointment(appointment_id: str, appointment_data: AppointmentUpdate):
    appointment = get_appointment_by_id(appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Update only provided fields
    update_data = appointment_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        appointment[field] = value
    
    appointment["updated_at"] = datetime.now()
    return appointment

# Office Visit routes
@router.post("/office-visits", response_model=OfficeVisit)
async def create_office_visit(visit_data: OfficeVisitCreate):
    visit_id = str(uuid.uuid4())
    visit = {
        "id": visit_id,
        "appointment_id": visit_data.appointment_id,
        "patient_id": visit_data.patient_id,
        "doctor_id": visit_data.doctor_id,
        "nurse_id": visit_data.nurse_id,
        "visit_type": visit_data.visit_type,
        "chief_complaint": visit_data.chief_complaint,
        "vital_signs": visit_data.vital_signs,
        "examination_notes": visit_data.examination_notes,
        "diagnosis": visit_data.diagnosis,
        "treatment_plan": visit_data.treatment_plan,
        "prescriptions": visit_data.prescriptions,
        "follow_up_date": visit_data.follow_up_date,
        "visit_date": datetime.now(),
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    office_visits_db[visit_id] = visit
    return visit

@router.get("/office-visits", response_model=List[OfficeVisit])
async def get_office_visits(skip: int = 0, limit: int = 100):
    visits = list(office_visits_db.values())
    return visits[skip : skip + limit]

@router.get("/office-visits/{visit_id}", response_model=OfficeVisit)
async def get_office_visit(visit_id: str):
    visit = office_visits_db.get(visit_id)
    if not visit:
        raise HTTPException(status_code=404, detail="Office visit not found")
    return visit

# Schedule routes
@router.post("/schedules", response_model=Schedule)
async def create_schedule(schedule_data: ScheduleCreate):
    schedule_id = str(uuid.uuid4())
    schedule = {
        "id": schedule_id,
        "doctor_id": schedule_data.doctor_id,
        "date": schedule_data.date,
        "start_time": schedule_data.start_time,
        "end_time": schedule_data.end_time,
        "is_available": schedule_data.is_available,
        "notes": schedule_data.notes,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    schedules_db[schedule_id] = schedule
    return schedule

@router.get("/schedules/available-slots")
async def get_available_slots(doctor_id: str, date: datetime, duration_minutes: int = 30):
    # Mock implementation - replace with real logic
    available_slots = [
        {"start_time": "09:00", "end_time": "09:30"},
        {"start_time": "09:30", "end_time": "10:00"},
        {"start_time": "10:00", "end_time": "10:30"},
        {"start_time": "14:00", "end_time": "14:30"},
        {"start_time": "14:30", "end_time": "15:00"},
    ]
    
    return {
        "doctor_id": doctor_id,
        "date": date,
        "duration_minutes": duration_minutes,
        "available_slots": available_slots
    }

# Dashboard routes
@router.get("/dashboard/stats")
async def get_dashboard_stats():
    total_patients = len(patients_db)
    total_appointments = len(appointments_db)
    total_doctors = len(doctors_db)
    today_appointments = len([
        apt for apt in appointments_db.values()
        if apt["scheduled_date"].date() == datetime.now().date()
    ])
    
    return {
        "total_patients": total_patients,
        "total_appointments": total_appointments,
        "total_doctors": total_doctors,
        "today_appointments": today_appointments,
        "timestamp": datetime.now()
    }

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "LotusHealth Clinic Service"}
