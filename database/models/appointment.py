from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .base import Base

class Appointment(Base):
    __tablename__ = 'appointments'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey('patients.id'), nullable=False)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey('doctors.id'), nullable=False)
    appointment_type = Column(String(50), nullable=False)  # office_visit, consultation, follow_up, emergency, routine_checkup
    status = Column(String(20), default='scheduled')  # scheduled, confirmed, in_progress, completed, cancelled, no_show
    scheduled_date = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=30)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # LLM Integration fields
    ai_notes = Column(Text, nullable=True)  # AI-generated notes and insights
    risk_assessment = Column(JSON, nullable=True)  # AI risk assessment
    follow_up_recommendations = Column(Text, nullable=True)  # AI-generated follow-up suggestions
    
    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    # office_visit = relationship("OfficeVisit", back_populates="appointment", uselist=False)  # Commented out - table doesn't exist
