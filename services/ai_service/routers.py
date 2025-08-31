"""
AI Service - API Routes
Handles all AI-related API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
import time
import sys
import os

# Add project root to path to import shared models
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from shared.models import PatientNoteInput
from .graph import build_graph, build_simple_graph
from .state import WorkflowState, WorkflowResult

router = APIRouter(prefix="/ai", tags=["artificial-intelligence"])

# Initialize workflow graphs
full_workflow = build_graph()
simple_workflow = build_simple_graph()

@router.get("/health")
async def health_check():
    """Health check for AI service"""
    return {
        "status": "healthy", 
        "service": "LotusHealth AI Service",
        "workflow_version": "1.0.0",
        "available_workflows": ["simple", "full"]
    }

@router.post("/process-note/simple")
async def process_note_simple(note_input: PatientNoteInput):
    """
    Process patient note using simple workflow (3 agents)
    - Parser: Extract structured data
    - Evaluator: Validate medical terminology
    - Synthesizer: Generate patient report
    """
    start_time = time.time()
    
    try:
        # Create workflow state
        state = WorkflowState(
            note=note_input.note,
            session_id=note_input.session_id
        )
        
        # Execute simple workflow
        result = simple_workflow.invoke(state)
        
        processing_time = time.time() - start_time
        
        return {
            "session_id": note_input.session_id,
            "success": True,
            "workflow_type": "simple",
            "patient_report": result.get("report"),
            "processing_time": processing_time,
            "timestamp": result.get("timestamp")
        }
        
    except Exception as e:
        processing_time = time.time() - start_time
        raise HTTPException(
            status_code=500,
            detail=f"AI processing failed: {str(e)}"
        )

@router.post("/process-note/full")
async def process_note_full(note_input: PatientNoteInput):
    """
    Process patient note using full workflow (5 agents)
    - Parser: Extract structured data
    - Evaluator: Validate medical terminology
    - Synthesizer: Generate patient report
    - Risk Assessor: Evaluate risk factors
    - Treatment Planner: Suggest treatment approaches
    """
    start_time = time.time()
    
    try:
        # Create workflow state
        state = WorkflowState(
            note=note_input.note,
            session_id=note_input.session_id
        )
        
        # Execute full workflow
        result = full_workflow.invoke(state)
        
        processing_time = time.time() - start_time
        
        return {
            "session_id": note_input.session_id,
            "success": True,
            "workflow_type": "full",
            "patient_report": result.get("report"),
            "risk_assessment": result.get("risk_assessment"),
            "treatment_recommendations": result.get("treatment_plan"),
            "agent_results": result.get("agent_results", []),
            "processing_time": processing_time,
            "timestamp": result.get("timestamp"),
            "errors": result.get("errors", []),
            "warnings": result.get("warnings", [])
        }
        
    except Exception as e:
        processing_time = time.time() - start_time
        raise HTTPException(
            status_code=500,
            detail=f"AI processing failed: {str(e)}"
        )

@router.post("/analyze-symptoms")
async def analyze_symptoms(symptoms: str, patient_context: Optional[str] = None):
    """
    Analyze patient symptoms and provide insights
    """
    try:
        # Create a note-like input from symptoms
        note = f"Symptoms: {symptoms}"
        if patient_context:
            note += f"\nPatient Context: {patient_context}"
        
        # Use simple workflow for symptom analysis
        state = WorkflowState(note=note)
        result = simple_workflow.invoke(state)
        
        return {
            "symptoms": symptoms,
            "analysis": result.get("report"),
            "confidence_score": 0.85,
            "recommendations": [
                "Consult with healthcare provider",
                "Monitor symptoms",
                "Follow up if symptoms worsen"
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Symptom analysis failed: {str(e)}"
        )

@router.post("/generate-treatment-plan")
async def generate_treatment_plan(diagnosis: str, patient_data: Dict[str, Any]):
    """
    Generate treatment plan based on diagnosis and patient data
    """
    try:
        # Create a note-like input for treatment planning
        note = f"Diagnosis: {diagnosis}\nPatient Data: {patient_data}"
        
        # Use full workflow to get treatment recommendations
        state = WorkflowState(note=note)
        result = full_workflow.invoke(state)
        
        return {
            "diagnosis": diagnosis,
            "treatment_plan": result.get("treatment_plan"),
            "risk_assessment": result.get("risk_assessment"),
            "confidence_score": 0.8,
            "disclaimer": "This is AI-generated information. Always consult healthcare professionals."
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Treatment planning failed: {str(e)}"
        )

@router.get("/workflow-info")
async def get_workflow_info():
    """Get information about available AI workflows"""
    return {
        "workflows": {
            "simple": {
                "description": "Basic note processing with 3 agents",
                "agents": ["parser", "evaluator", "synthesizer"],
                "use_case": "Quick patient note analysis",
                "processing_time": "~10-30 seconds"
            },
            "full": {
                "description": "Comprehensive analysis with 5 agents",
                "agents": ["parser", "evaluator", "synthesizer", "risk_assessor", "treatment_planner"],
                "use_case": "Complete patient assessment and treatment planning",
                "processing_time": "~30-60 seconds"
            }
        },
        "capabilities": [
            "Extract medical entities from notes",
            "Validate medical terminology",
            "Generate patient-friendly reports",
            "Assess patient risk factors",
            "Suggest treatment approaches",
            "Provide ICD-10 and SNOMED codes"
        ],
        "disclaimer": "AI-generated medical information should be reviewed by healthcare professionals"
    }

@router.post("/validate-medical-data")
async def validate_medical_data(medical_data: Dict[str, Any]):
    """
    Validate medical data against standards
    """
    try:
        # Use evaluator agent directly
        from .agents import evaluator_agent
        from langchain_openai import ChatOpenAI
        
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        evaluator = evaluator_agent(llm)
        result = evaluator(str(medical_data))
        
        return {
            "validation_result": result.content if hasattr(result, 'content') else str(result),
            "confidence_score": 0.85
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Medical data validation failed: {str(e)}"
        )
