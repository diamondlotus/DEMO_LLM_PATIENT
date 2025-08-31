from sqlalchemy import Column, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSON
from datetime import datetime
import uuid
from .base import Base

class PatientEducation(Base):
    __tablename__ = 'patient_education'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey('patients.id'), nullable=False)
    topic = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    difficulty_level = Column(String(20), nullable=False)  # basic, intermediate, advanced
    language = Column(String(10), default='en')
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # LLM Integration fields
    ai_generated = Column(Boolean, default=False)  # Whether content was AI-generated
    personalization_factors = Column(JSON, nullable=True)  # Factors used for personalization
    comprehension_check = Column(JSON, nullable=True)  # AI-generated comprehension questions
