from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .base import Base

class MedicalRecord(Base):
    __tablename__ = 'medical_records'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey('patients.id'), nullable=False)
    # office_visit_id = Column(UUID(as_uuid=True), ForeignKey('office_visits.id'), nullable=True)  # Commented out - table doesn't exist
    record_type = Column(String(50), nullable=False)  # diagnosis, treatment, lab_result, imaging, medication
    content = Column(Text, nullable=False)
    record_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # LLM Integration fields
    content_embedding = Column(JSON, nullable=True)  # Vector embedding for semantic search
    ai_summary = Column(Text, nullable=True)  # AI-generated summary
    related_conditions = Column(ARRAY(String), nullable=True)  # AI-identified related conditions
    
    # Relationships
    patient = relationship("Patient", back_populates="medical_records")
    # office_visit = relationship("OfficeVisit", back_populates="medical_records")  # Commented out - table doesn't exist
