"""
LotusHealth AI Service - Main Application
Clean main.py that only contains app configuration and router inclusion
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from routers import router as ai_router

# Create FastAPI app
app = FastAPI(title="LotusHealth AI Service", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ai_router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "LotusHealth AI Service", 
        "version": "1.0.0",
        "description": "Multi-Agent AI System for Healthcare",
        "endpoints": {
            "health": "/ai/health",
            "process_note_simple": "/ai/process-note/simple",
            "process_note_full": "/ai/process-note/full",
            "analyze_symptoms": "/ai/analyze-symptoms",
            "generate_treatment_plan": "/ai/generate-treatment-plan",
            "workflow_info": "/ai/workflow-info",
            "validate_medical_data": "/ai/validate-medical-data"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
