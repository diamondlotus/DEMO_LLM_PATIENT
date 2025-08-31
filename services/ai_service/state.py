"""
AI Service - Workflow State Management
Defines the state structure for multi-agent workflow
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class WorkflowState(BaseModel):
    """State for the multi-agent workflow"""
    
    # Input
    note: str = Field(..., description="Patient note input")
    session_id: Optional[str] = Field(None, description="Session identifier")
    
    # Parser Agent Output
    data: Optional[Dict[str, Any]] = Field(None, description="Parsed structured data")
    
    # Evaluator Agent Output
    validated_data: Optional[Dict[str, Any]] = Field(None, description="Validated medical data")
    
    # Synthesizer Agent Output
    report: Optional[Dict[str, Any]] = Field(None, description="Final patient report")
    
    # Risk Assessment Agent Output
    risk_assessment: Optional[Dict[str, Any]] = Field(None, description="Risk assessment results")
    
    # Treatment Planning Agent Output
    treatment_plan: Optional[Dict[str, Any]] = Field(None, description="Treatment recommendations")
    
    # Metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Processing timestamp")
    workflow_version: str = Field("1.0.0", description="Workflow version")
    processing_time: Optional[float] = Field(None, description="Total processing time in seconds")
    
    # Error handling
    errors: List[str] = Field(default_factory=list, description="List of processing errors")
    warnings: List[str] = Field(default_factory=list, description="List of processing warnings")
    
    class Config:
        arbitrary_types_allowed = True

class AgentResult(BaseModel):
    """Result from an individual agent"""
    
    agent_name: str = Field(..., description="Name of the agent")
    success: bool = Field(..., description="Whether the agent succeeded")
    output: Optional[Dict[str, Any]] = Field(None, description="Agent output")
    error: Optional[str] = Field(None, description="Error message if failed")
    processing_time: float = Field(..., description="Time taken by this agent")
    confidence_score: Optional[float] = Field(None, description="Confidence in the result")
    
    class Config:
        arbitrary_types_allowed = True

class WorkflowResult(BaseModel):
    """Complete workflow result"""
    
    session_id: str = Field(..., description="Session identifier")
    success: bool = Field(..., description="Whether the workflow succeeded")
    patient_report: Optional[Dict[str, Any]] = Field(None, description="Final patient report")
    risk_assessment: Optional[Dict[str, Any]] = Field(None, description="Risk assessment")
    treatment_recommendations: Optional[Dict[str, Any]] = Field(None, description="Treatment plan")
    agent_results: List[AgentResult] = Field(default_factory=list, description="Results from each agent")
    total_processing_time: float = Field(..., description="Total workflow time")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Completion timestamp")
    workflow_version: str = Field("1.0.0", description="Workflow version used")
    
    class Config:
        arbitrary_types_allowed = True
