from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .base import Base

class OfficeVisit(Base):
    __tablename__ = 'office_visits'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    appointment_id = Column(UUID(as_uuid=True), ForeignKey('appointments.id'), nullable=True)
    patient_id = Column(UUID(as_uuid=True), ForeignKey('patients.id'), nullable=False)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey('doctors.id'), nullable=False)
    nurse_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    visit_type = Column(String(50), nullable=False)  # new_patient, established_patient, urgent_care, specialist_consultation
    chief_complaint = Column(Text, nullable=False)
    vital_signs = Column(JSON, nullable=True)
    examination_notes = Column(Text, nullable=True)
    diagnosis = Column(Text, nullable=True)
    treatment_plan = Column(Text, nullable=True)
    prescriptions = Column(ARRAY(String), nullable=True)
    follow_up_date = Column(DateTime, nullable=True)
    visit_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # LLM Integration fields
    ai_diagnosis_support = Column(JSON, nullable=True)  # AI diagnostic suggestions
    treatment_alternatives = Column(JSON, nullable=True)  # AI-suggested treatment alternatives
    drug_interaction_check = Column(JSON, nullable=True)  # AI drug interaction analysis
    clinical_guidelines = Column(JSON, nullable=True)  # Relevant clinical guidelines
    
    # Relationships - Commented out because table doesn't exist
    # appointment = relationship("Appointment", back_populates="office_visit")
    # patient = relationship("Patient", back_populates="office_visits")
    # doctor = relationship("Doctor", back_populates="office_visits")
    # nurse = relationship("User", foreign_keys=[nurse_id])
    # medical_records = relationship("MedicalRecord", back_populates="office_visit")
