from sqlalchemy import Column, String, DateTime, Text, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .base import Base

class LLMInteraction(Base):
    __tablename__ = 'llm_interactions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey('patients.id'), nullable=True)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey('doctors.id'), nullable=True)
    interaction_type = Column(String(50), nullable=False)  # diagnosis_support, treatment_planning, risk_assessment, patient_education
    user_input = Column(Text, nullable=False)
    llm_response = Column(Text, nullable=False)
    context = Column(JSON, nullable=True)  # Patient context, medical history, etc.
    confidence_score = Column(Float, nullable=True)  # LLM confidence in response
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="llm_interactions")
    # doctor = relationship("Doctor", back_populates="llm_interactions")  # Commented out - table doesn't exist
