from sqlalchemy import Column, String, DateTime, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSON
from datetime import datetime
import uuid
from .base import Base

class KnowledgeBase(Base):
    __tablename__ = 'knowledge_base'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category = Column(String(100), nullable=False)  # medical_guidelines, drug_info, disease_info, treatment_protocols
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    source = Column(String(200), nullable=True)
    version = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # LLM Integration fields
    content_embedding = Column(JSON, nullable=True)  # Vector embedding for semantic search
    keywords = Column(ARRAY(String), nullable=True)  # AI-extracted keywords
    related_topics = Column(ARRAY(String), nullable=True)  # AI-identified related topics
