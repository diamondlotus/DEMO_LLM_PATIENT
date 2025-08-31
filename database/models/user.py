from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .base import Base

class User(Base):
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False)  # admin, doctor, nurse, receptionist, patient
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    doctor_appointments = relationship("Appointment", foreign_keys="Appointment.doctor_id", back_populates="doctor")
    nurse_visits = relationship("OfficeVisit", foreign_keys="OfficeVisit.nurse_id", back_populates="nurse")
    patient_appointments = relationship("Appointment", foreign_keys="Appointment.patient_id", back_populates="patient")
    patient_visits = relationship("OfficeVisit", foreign_keys="OfficeVisit.patient_id", back_populates="patient")
