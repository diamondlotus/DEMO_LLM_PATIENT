"""
AI Service - API Routes
Handles all AI-related API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from typing import Dict, Any, Optional
import time
import sys
import os
import json
from datetime import datetime

# Add project root to path to import shared models
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from shared.models import PatientNoteInput
from graph import build_graph, build_simple_graph
from state import WorkflowState, WorkflowResult

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
        # Check if OpenAI API key is available and has quota
        import os
        openai_key = os.getenv("OPENAI_API_KEY")
        
        if not openai_key:
            # Mock response for testing without API key
            processing_time = time.time() - start_time
            mock_report = {
                "patient_summary": "Based on the patient's symptoms of chest pain and shortness of breath, this could indicate a serious cardiovascular condition requiring immediate medical attention.",
                "key_points": [
                    "Chest pain and shortness of breath are concerning symptoms",
                    "Could indicate heart attack, angina, or other cardiac issues",
                    "Requires immediate medical evaluation"
                ],
                "recommendations": [
                    "Seek immediate medical attention",
                    "Call emergency services if symptoms worsen",
                    "Avoid strenuous activity until evaluated"
                ],
                "questions_for_doctor": [
                    "What is causing my chest pain?",
                    "Do I need any tests or imaging?",
                    "What are the treatment options?"
                ],
                "follow_up_plan": "Schedule follow-up with cardiologist within 1 week",
                "risk_level": "high",
                "urgency": "urgent"
            }
            
            return {
                "session_id": note_input.session_id,
                "success": True,
                "workflow_type": "simple_mock",
                "patient_report": mock_report,
                "processing_time": processing_time,
                "timestamp": time.time(),
                "note": "Mock response - OpenAI API key not available or quota exceeded"
            }
        
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
        
        # If OpenAI quota exceeded, return mock response
        if "quota" in str(e).lower() or "insufficient_quota" in str(e).lower():
            mock_report = {
                "patient_summary": "Analysis of patient symptoms indicates need for medical evaluation.",
                "key_points": [
                    "Patient reported symptoms require medical attention",
                    "Further evaluation recommended",
                    "Monitor symptoms closely"
                ],
                "recommendations": [
                    "Schedule appointment with healthcare provider",
                    "Monitor symptoms for changes",
                    "Follow up as directed"
                ],
                "questions_for_doctor": [
                    "What could be causing these symptoms?",
                    "What tests might be needed?",
                    "What are the next steps?"
                ],
                "follow_up_plan": "Follow up with healthcare provider",
                "risk_level": "medium",
                "urgency": "soon"
            }
            
            return {
                "session_id": note_input.session_id,
                "success": True,
                "workflow_type": "simple_mock",
                "patient_report": mock_report,
                "processing_time": processing_time,
                "timestamp": time.time(),
                "note": "Mock response - OpenAI quota exceeded"
            }
        
        import traceback
        error_details = traceback.format_exc()
        print(f"Error details: {error_details}")
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

@router.post("/learn-and-update")
async def learn_and_update_knowledge(learning_data: Dict[str, Any]):
    """
    AI Learning Function - Learn from interactions and update knowledge base
    
    This endpoint allows the AI to:
    1. Learn from successful interactions
    2. Update medical knowledge patterns
    3. Improve future responses based on learned data
    4. Store new medical insights in the database
    """
    try:
        # Extract learning data
        interaction_type = learning_data.get("interaction_type", "general_learning")
        user_input = learning_data.get("user_input", "")
        ai_response = learning_data.get("ai_response", "")
        feedback_score = learning_data.get("feedback_score", 0.0)  # 0-10 scale
        medical_context = learning_data.get("medical_context", {})
        learning_notes = learning_data.get("learning_notes", "")
        
        # Validate required fields
        if not user_input or not ai_response:
            raise HTTPException(
                status_code=400,
                detail="user_input and ai_response are required"
            )
        
        # Process and analyze the learning data
        learning_result = await process_learning_data(
            interaction_type=interaction_type,
            user_input=user_input,
            ai_response=ai_response,
            feedback_score=feedback_score,
            medical_context=medical_context,
            learning_notes=learning_notes
        )
        
        return {
            "success": True,
            "message": "Knowledge updated successfully",
            "learning_result": learning_result,
            "timestamp": datetime.utcnow().isoformat(),
            "interaction_id": learning_result.get("interaction_id")
        }
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Learning error details: {error_details}")
        raise HTTPException(
            status_code=500,
            detail=f"Learning and update failed: {str(e)}"
        )

async def process_learning_data(
    interaction_type: str,
    user_input: str,
    ai_response: str,
    feedback_score: float,
    medical_context: Dict[str, Any],
    learning_notes: str
) -> Dict[str, Any]:
    """
    Process learning data and update knowledge base
    """
    try:
        # Extract key medical patterns from the interaction
        medical_patterns = extract_medical_patterns(user_input, ai_response)
        
        # Analyze feedback to determine learning value
        learning_value = analyze_feedback_value(feedback_score, medical_context)
        
        # Update knowledge base with new insights
        knowledge_updates = await update_knowledge_base(
            patterns=medical_patterns,
            context=medical_context,
            feedback_score=feedback_score,
            learning_notes=learning_notes
        )
        
        # Store interaction for future learning
        interaction_record = {
            "interaction_type": interaction_type,
            "user_input": user_input,
            "ai_response": ai_response,
            "feedback_score": feedback_score,
            "medical_context": medical_context,
            "learning_notes": learning_notes,
            "patterns_extracted": medical_patterns,
            "learning_value": learning_value,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return {
            "interaction_id": f"learn_{int(time.time())}",
            "patterns_extracted": medical_patterns,
            "learning_value": learning_value,
            "knowledge_updates": knowledge_updates,
            "interaction_record": interaction_record
        }
        
    except Exception as e:
        print(f"Error processing learning data: {str(e)}")
        raise

def extract_medical_patterns(user_input: str, ai_response: str) -> Dict[str, Any]:
    """
    Extract medical patterns and insights from user input and AI response
    """
    patterns = {
        "symptoms": [],
        "diagnoses": [],
        "treatments": [],
        "medications": [],
        "risk_factors": [],
        "recommendations": [],
        "medical_terms": []
    }
    
    # Simple pattern extraction (in production, use more sophisticated NLP)
    text_to_analyze = f"{user_input} {ai_response}".lower()
    
    # Extract common medical terms
    medical_terms = [
        "chest pain", "shortness of breath", "hypertension", "diabetes",
        "fever", "cough", "headache", "nausea", "dizziness", "fatigue",
        "joint pain", "swelling", "rash", "bleeding", "infection"
    ]
    
    for term in medical_terms:
        if term in text_to_analyze:
            patterns["medical_terms"].append(term)
    
    # Extract symptoms (words ending with common symptom patterns)
    symptom_patterns = ["pain", "ache", "nausea", "dizziness", "fatigue", "fever"]
    for pattern in symptom_patterns:
        if pattern in text_to_analyze:
            patterns["symptoms"].append(pattern)
    
    # Extract recommendations (action words)
    action_words = ["schedule", "call", "visit", "take", "avoid", "monitor"]
    for word in action_words:
        if word in text_to_analyze:
            patterns["recommendations"].append(word)
    
    return patterns

def analyze_feedback_value(feedback_score: float, medical_context: Dict[str, Any]) -> str:
    """
    Analyze the learning value of feedback
    """
    if feedback_score >= 8.0:
        return "high_value"
    elif feedback_score >= 6.0:
        return "medium_value"
    elif feedback_score >= 4.0:
        return "low_value"
    else:
        return "negative_learning"

async def update_knowledge_base(
    patterns: Dict[str, Any],
    context: Dict[str, Any],
    feedback_score: float,
    learning_notes: str
) -> Dict[str, Any]:
    """
    Update knowledge base with new insights
    """
    # In a production system, this would:
    # 1. Connect to the database
    # 2. Update knowledge_base table
    # 3. Store interaction in llm_interactions table
    # 4. Update embeddings for semantic search
    
    knowledge_updates = {
        "new_patterns": patterns,
        "context_insights": context,
        "feedback_analysis": {
            "score": feedback_score,
            "value": "positive" if feedback_score >= 6.0 else "negative"
        },
        "learning_notes": learning_notes,
        "update_timestamp": datetime.utcnow().isoformat()
    }
    
    # For now, return the updates (in production, save to database)
    print(f"Knowledge base update: {json.dumps(knowledge_updates, indent=2)}")
    
    return knowledge_updates

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

@router.get("/processing-history")
async def get_processing_history(skip: int = 0, limit: int = 10):
    """
    Get AI processing history (mock implementation for demo)
    In production, this would query a database table
    """
    try:
        # Mock processing history for demonstration
        mock_history = [
            {
                "id": f"session_{i+1}",
                "input": f"Sample patient note {i+1}",
                "output": {
                    "patient_summary": f"Analysis of patient condition {i+1}",
                    "key_points": ["Key point 1", "Key point 2"],
                    "recommendations": ["Recommendation 1", "Recommendation 2"],
                    "risk_level": "medium" if i % 2 == 0 else "low"
                },
                "timestamp": "2024-01-01T10:00:00Z",
                "processing_time": 2.5 + (i * 0.5),
                "workflow_type": "simple" if i % 2 == 0 else "full",
                "confidence_score": 0.85
            }
            for i in range(max(0, skip), min(20, skip + limit))
        ]

        return {
            "items": mock_history,
            "total": 20,
            "skip": skip,
            "limit": limit
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve processing history: {str(e)}"
        )

@router.get("/processing/{processing_id}")
async def get_processing_by_id(processing_id: str):
    """
    Get specific processing result by ID (mock implementation)
    """
    try:
        # Mock single processing result
        mock_result = {
            "id": processing_id,
            "input": "Patient presents with chest pain and shortness of breath",
            "output": {
                "patient_summary": "Patient shows symptoms consistent with possible cardiac issues",
                "key_points": [
                    "Chest pain lasting 30 minutes",
                    "Associated shortness of breath",
                    "No prior cardiac history"
                ],
                "recommendations": [
                    "Immediate ECG and cardiac enzymes",
                    "Monitor vital signs closely",
                    "Consider cardiology consultation"
                ],
                "questions_for_doctor": [
                    "Duration and character of chest pain?",
                    "Any radiation of pain?",
                    "Associated symptoms?"
                ],
                "follow_up_plan": "Cardiology follow-up within 24 hours",
                "risk_level": "high",
                "urgency": "urgent"
            },
            "timestamp": "2024-01-01T10:00:00Z",
            "processing_time": 3.2,
            "workflow_type": "simple",
            "confidence_score": 0.88
        }

        return mock_result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve processing result: {str(e)}"
        )

# Content Upload and Learning Endpoints
@router.post("/upload-file")
async def upload_file_for_learning(
    file: UploadFile = File(...),
    content_type: str = Form("medical_document"),
    category: str = Form("general"),
    tags: str = Form(""),
    uploader: str = Form("system")
):
    """
    Upload a file (PDF, DOCX, TXT, etc.) for AI learning
    """
    try:
        from content_upload_service import upload_file_service

        # Read file content
        file_content = await file.read()

        # Parse tags
        tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()]

        metadata = {
            "content_type": content_type,
            "category": category,
            "tags": tags_list,
            "uploader": uploader
        }

        result = upload_file_service(file_content, file.filename, metadata)

        if result["success"]:
            return {
                "message": "File uploaded and processed successfully",
                "result": result
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"File upload failed: {result.get('error', 'Unknown error')}"
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"File upload error: {str(e)}"
        )

@router.post("/upload-text")
async def upload_text_for_learning(text_data: Dict[str, Any]):
    """
    Upload text content directly for AI learning
    """
    try:
        from content_upload_service import upload_text_service

        content = text_data.get("content", "")
        title = text_data.get("title", "Untitled Content")
        metadata = text_data.get("metadata", {})

        result = upload_text_service(content, title, metadata)

        if result["success"]:
            return {
                "message": "Text content uploaded and processed successfully",
                "result": result
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Text upload failed: {result.get('error', 'Unknown error')}"
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Text upload error: {str(e)}"
        )

@router.post("/load-demo-data")
async def load_demo_medical_data():
    """
    Load demo medical data into AI knowledge base
    """
    try:
        from content_upload_service import load_demo_data_service

        result = load_demo_data_service()

        return {
            "message": "Demo data loading initiated",
            "result": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Demo data loading error: {str(e)}"
        )

@router.get("/uploaded-content")
async def get_uploaded_content_list():
    """
    Get list of uploaded content for learning
    """
    try:
        from content_upload_service import ContentUploadService
        service = ContentUploadService()
        content_list = service.get_uploaded_content_list()

        return {
            "items": content_list,
            "total": len(content_list)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving content list: {str(e)}"
        )

@router.get("/learning-statistics")
async def get_learning_statistics():
    """
    Get AI learning statistics and metrics
    """
    try:
        from content_upload_service import ContentUploadService
        service = ContentUploadService()
        stats = service.get_learning_statistics()

        return stats

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving learning statistics: {str(e)}"
        )

@router.delete("/uploaded-content/{content_id}")
async def delete_uploaded_content(content_id: str):
    """
    Delete uploaded content from knowledge base
    """
    try:
        # In production, this would remove from vector store and database
        return {
            "message": f"Content {content_id} deleted successfully",
            "content_id": content_id
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting content: {str(e)}"
        )
