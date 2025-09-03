"""
AI Service - Multi-Agent System for Healthcare
Agents for parsing, evaluating, and synthesizing patient notes
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, Any
import sys
import os

# Add project root to path to import shared models
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from shared.models import PatientNoteInput

# 1. Parser Agent - Extract structured entities from patient notes
def parser_agent(llm):
    prompt = ChatPromptTemplate.from_template(
        """You are a medical AI assistant. Extract structured medical information from patient notes.
        
        Extract and return JSON with the following structure:
        {{
            "diagnoses": ["list of diagnoses"],
            "medications": ["list of medications"],
            "lab_values": ["list of lab values"],
            "symptoms": ["list of symptoms"],
            "vital_signs": {{"blood_pressure": "value", "heart_rate": "value", "temperature": "value"}},
            "allergies": ["list of allergies"],
            "family_history": ["relevant family history"],
            "lifestyle_factors": ["diet", "exercise", "smoking", "alcohol"]
        }}
        
        Patient Note: {note}
        
        Return only valid JSON."""
    )
    return lambda note: llm.invoke(prompt.format_messages(note=note))

# 2. Evaluator Agent - Validate terminology and medical accuracy
def evaluator_agent(llm):
    prompt = ChatPromptTemplate.from_template(
        """You are a medical AI validator. Validate the structured medical data against medical standards.
        
        Validate and return JSON with:
        {{
            "validity_score": 0.0-1.0,
            "icd10_codes": ["suggested ICD-10 codes"],
            "snomed_codes": ["suggested SNOMED codes"],
            "validation_notes": ["validation findings"],
            "confidence_level": "high|medium|low",
            "recommendations": ["suggestions for improvement"]
        }}
        
        Structured Data: {data}
        
        Return only valid JSON."""
    )
    return lambda data: llm.invoke(prompt.format_messages(data=data))

# 3. Synthesizer Agent - Generate patient-friendly summary
def synthesizer_agent(llm):
    prompt = ChatPromptTemplate.from_template(
        """You are a medical AI educator. Generate a patient-friendly health report.
        
        Create a comprehensive but simple report including:
        {{
            "patient_summary": "Simple explanation of findings",
            "key_points": ["main health points"],
            "recommendations": ["action items for patient"],
            "questions_for_doctor": ["questions patient should ask"],
            "follow_up_plan": "next steps",
            "risk_level": "low|medium|high",
            "urgency": "routine|soon|urgent|emergency"
        }}
        
        Validated Data: {validated_data}
        
        Use simple language appropriate for patients. Return only valid JSON."""
    )
    return lambda validated_data: llm.invoke(prompt.format_messages(validated_data=validated_data))

# 4. Risk Assessment Agent - Assess patient risk factors
def risk_assessment_agent(llm):
    prompt = ChatPromptTemplate.from_template(
        """You are a medical AI risk assessor. Evaluate patient risk factors.
        
        Assess and return JSON with:
        {{
            "overall_risk": "low|medium|high",
            "risk_factors": ["identified risk factors"],
            "risk_score": 0.0-1.0,
            "preventive_measures": ["suggested preventive actions"],
            "monitoring_needs": ["what to monitor"],
            "red_flags": ["warning signs to watch for"]
        }}
        
        Patient Data: {patient_data}
        
        Return only valid JSON."""
    )
    return lambda patient_data: llm.invoke(prompt.format_messages(patient_data=patient_data))

# 5. Treatment Planning Agent - Suggest treatment approaches
def treatment_planning_agent(llm):
    prompt = ChatPromptTemplate.from_template(
        """You are a medical AI treatment planner. Suggest evidence-based treatment approaches.
        
        Suggest and return JSON with:
        {{
            "treatment_options": ["list of treatment approaches"],
            "evidence_level": "high|medium|low",
            "side_effects": ["potential side effects"],
            "contraindications": ["when not to use"],
            "monitoring_plan": ["what to monitor"],
            "success_metrics": ["how to measure success"],
            "alternative_treatments": ["alternative approaches"]
        }}
        
        Diagnosis and Patient Data: {diagnosis_data}
        
        Return only valid JSON."""
    )
    return lambda diagnosis_data: llm.invoke(prompt.format_messages(diagnosis_data=diagnosis_data))
