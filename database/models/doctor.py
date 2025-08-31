from sqlalchemy import Column, String, DateTime, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .base import Base

class Doctor(Base):
    __tablename__ = 'doctors'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    specialization = Column(String(100), nullable=False)
    license_number = Column(String(50), unique=True, nullable=False)
    years_experience = Column(Integer, nullable=True)
    education = Column(ARRAY(String), nullable=True)
    certifications = Column(ARRAY(String), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # LLM Integration fields
    expertise_embedding = Column(JSON, nullable=True)  # Embeddings of doctor's expertise
    ai_assistant_enabled = Column(Boolean, default=True)  # Whether AI assistant is enabled
    
    # Relationships
    appointments = relationship("Appointment", back_populates="doctor")
    office_visits = relationship("OfficeVisit", back_populates="doctor")
    schedules = relationship("Schedule", back_populates="doctor")
    llm_interactions = relationship("LLMInteraction", back_populates="doctor")
