"""
Database models package
"""

from .base import Base
from .user import User
from .patient import Patient
from .doctor import Doctor
from .appointment import Appointment
# from .office_visit import OfficeVisit  # Commented out - table doesn't exist
from .schedule import Schedule
from .medical_record import MedicalRecord
from .llm_interaction import LLMInteraction
from .knowledge_base import KnowledgeBase
from .patient_education import PatientEducation

__all__ = [
    "Base",
    "User", 
    "Patient",
    "Doctor",
    "Appointment",
    # "OfficeVisit",  # Commented out - table doesn't exist
    "Schedule",
    "MedicalRecord",
    "LLMInteraction",
    "KnowledgeBase",
    "PatientEducation"
]