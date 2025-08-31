from sqlalchemy import Column, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .base import Base

class Schedule(Base):
    __tablename__ = 'schedules'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey('doctors.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    start_time = Column(String(10), nullable=False)
    end_time = Column(String(10), nullable=False)
    is_available = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    doctor = relationship("Doctor", back_populates="schedules")
