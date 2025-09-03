from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .base import Base

class Patient(Base):
    __tablename__ = 'patients'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    gender = Column(String(10), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=False)
    address = Column(Text, nullable=False)
    emergency_contact = Column(String(100), nullable=False)
    insurance_info = Column(JSON, nullable=True)
    medical_history = Column(Text, nullable=True)
    allergies = Column(ARRAY(String), nullable=True)
    medications = Column(ARRAY(String), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # LLM Integration fields
    medical_notes_embedding = Column(JSON, nullable=True)  # Store embeddings for semantic search
    risk_factors = Column(JSON, nullable=True)  # AI-identified risk factors
    treatment_recommendations = Column(JSON, nullable=True)  # AI-generated recommendations
    
    # Relationships
    user = relationship("User", back_populates="patient_profile")
    appointments = relationship("Appointment", back_populates="patient")
    # office_visits = relationship("OfficeVisit", back_populates="patient")  # Commented out - table doesn't exist
    medical_records = relationship("MedicalRecord", back_populates="patient")
    llm_interactions = relationship("LLMInteraction", back_populates="patient")
