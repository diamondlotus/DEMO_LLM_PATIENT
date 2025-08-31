"""
AI Service - Workflow Graph Orchestration
Defines the multi-agent workflow using LangGraph
"""

import time
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from .agents import (
    parser_agent, evaluator_agent, synthesizer_agent,
    risk_assessment_agent, treatment_planning_agent
)
from .state import WorkflowState, AgentResult
import os

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.1,  # Low temperature for medical accuracy
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

def build_graph():
    """Build the multi-agent workflow graph"""
    
    workflow = StateGraph(WorkflowState)
    
    # Initialize agents
    parse = parser_agent(llm)
    evaluate = evaluator_agent(llm)
    synthesize = synthesizer_agent(llm)
    assess_risk = risk_assessment_agent(llm)
    plan_treatment = treatment_planning_agent(llm)
    
    # Define node functions with timing and error handling
    def parse_node(state: WorkflowState) -> Dict[str, Any]:
        """Parse patient note into structured data"""
        start_time = time.time()
        try:
            result = parse(state.note)
            processing_time = time.time() - start_time
            
            # Create agent result
            agent_result = AgentResult(
                agent_name="parser",
                success=True,
                output=result.content if hasattr(result, 'content') else str(result),
                processing_time=processing_time,
                confidence_score=0.9
            )
            
            return {
                "data": result.content if hasattr(result, 'content') else str(result),
                "agent_results": [agent_result]
            }
        except Exception as e:
            processing_time = time.time() - start_time
            agent_result = AgentResult(
                agent_name="parser",
                success=False,
                error=str(e),
                processing_time=processing_time
            )
            return {
                "data": None,
                "errors": [f"Parser failed: {str(e)}"],
                "agent_results": [agent_result]
            }
    
    def evaluate_node(state: WorkflowState) -> Dict[str, Any]:
        """Evaluate and validate medical data"""
        start_time = time.time()
        try:
            result = evaluate(state.data)
            processing_time = time.time() - start_time
            
            agent_result = AgentResult(
                agent_name="evaluator",
                success=True,
                output=result.content if hasattr(result, 'content') else str(result),
                processing_time=processing_time,
                confidence_score=0.85
            )
            
            return {
                "validated_data": result.content if hasattr(result, 'content') else str(result),
                "agent_results": state.agent_results + [agent_result]
            }
        except Exception as e:
            processing_time = time.time() - start_time
            agent_result = AgentResult(
                agent_name="evaluator",
                success=False,
                error=str(e),
                processing_time=processing_time
            )
            return {
                "validated_data": None,
                "errors": state.errors + [f"Evaluator failed: {str(e)}"],
                "agent_results": state.agent_results + [agent_result]
            }
    
    def synthesize_node(state: WorkflowState) -> Dict[str, Any]:
        """Generate patient-friendly summary"""
        start_time = time.time()
        try:
            result = synthesize(state.validated_data)
            processing_time = time.time() - start_time
            
            agent_result = AgentResult(
                agent_name="synthesizer",
                success=True,
                output=result.content if hasattr(result, 'content') else str(result),
                processing_time=processing_time,
                confidence_score=0.9
            )
            
            return {
                "report": result.content if hasattr(result, 'content') else str(result),
                "agent_results": state.agent_results + [agent_result]
            }
        except Exception as e:
            processing_time = time.time() - start_time
            agent_result = AgentResult(
                agent_name="synthesizer",
                success=False,
                error=str(e),
                processing_time=processing_time
            )
            return {
                "report": None,
                "errors": state.errors + [f"Synthesizer failed: {str(e)}"],
                "agent_results": state.agent_results + [agent_result]
            }
    
    def risk_assessment_node(state: WorkflowState) -> Dict[str, Any]:
        """Assess patient risk factors"""
        start_time = time.time()
        try:
            # Combine note and parsed data for risk assessment
            patient_data = {
                "note": state.note,
                "parsed_data": state.data
            }
            result = assess_risk(patient_data)
            processing_time = time.time() - start_time
            
            agent_result = AgentResult(
                agent_name="risk_assessor",
                success=True,
                output=result.content if hasattr(result, 'content') else str(result),
                processing_time=processing_time,
                confidence_score=0.8
            )
            
            return {
                "risk_assessment": result.content if hasattr(result, 'content') else str(result),
                "agent_results": state.agent_results + [agent_result]
            }
        except Exception as e:
            processing_time = time.time() - start_time
            agent_result = AgentResult(
                agent_name="risk_assessor",
                success=False,
                error=str(e),
                processing_time=processing_time
            )
            return {
                "risk_assessment": None,
                "errors": state.errors + [f"Risk assessment failed: {str(e)}"],
                "agent_results": state.agent_results + [agent_result]
            }
    
    def treatment_planning_node(state: WorkflowState) -> Dict[str, Any]:
        """Plan treatment approaches"""
        start_time = time.time()
        try:
            # Combine validated data and risk assessment for treatment planning
            diagnosis_data = {
                "validated_data": state.validated_data,
                "risk_assessment": state.risk_assessment
            }
            result = plan_treatment(diagnosis_data)
            processing_time = time.time() - start_time
            
            agent_result = AgentResult(
                agent_name="treatment_planner",
                success=True,
                output=result.content if hasattr(result, 'content') else str(result),
                processing_time=processing_time,
                confidence_score=0.85
            )
            
            return {
                "treatment_plan": result.content if hasattr(result, 'content') else str(result),
                "agent_results": state.agent_results + [agent_result]
            }
        except Exception as e:
            processing_time = time.time() - start_time
            agent_result = AgentResult(
                agent_name="treatment_planner",
                success=False,
                error=str(e),
                processing_time=processing_time
            )
            return {
                "treatment_plan": None,
                "errors": state.errors + [f"Treatment planning failed: {str(e)}"],
                "agent_results": state.agent_results + [agent_result]
            }
    
    # Add nodes to the graph
    workflow.add_node("parse", parse_node)
    workflow.add_node("evaluate", evaluate_node)
    workflow.add_node("synthesize", synthesize_node)
    workflow.add_node("assess_risk", risk_assessment_node)
    workflow.add_node("plan_treatment", treatment_planning_node)
    
    # Define workflow edges
    workflow.add_edge("parse", "evaluate")
    workflow.add_edge("evaluate", "synthesize")
    workflow.add_edge("evaluate", "assess_risk")
    workflow.add_edge("assess_risk", "plan_treatment")
    
    # Set entry and exit points
    workflow.set_entry_point("parse")
    workflow.set_finish_point("synthesize")
    workflow.set_finish_point("plan_treatment")
    
    return workflow.compile()

def build_simple_graph():
    """Build a simplified workflow for basic note processing"""
    
    workflow = StateGraph(WorkflowState)
    
    # Initialize basic agents
    parse = parser_agent(llm)
    evaluate = evaluator_agent(llm)
    synthesize = synthesizer_agent(llm)
    
    # Define simple node functions
    def parse_node(state: WorkflowState) -> Dict[str, Any]:
        result = parse(state.note)
        return {"data": result.content if hasattr(result, 'content') else str(result)}
    
    def evaluate_node(state: WorkflowState) -> Dict[str, Any]:
        result = evaluate(state.data)
        return {"validated_data": result.content if hasattr(result, 'content') else str(result)}
    
    def synthesize_node(state: WorkflowState) -> Dict[str, Any]:
        result = synthesize(state.validated_data)
        return {"report": result.content if hasattr(result, 'content') else str(result)}
    
    # Add nodes and edges
    workflow.add_node("parse", parse_node)
    workflow.add_node("evaluate", evaluate_node)
    workflow.add_node("synthesize", synthesize_node)
    
    workflow.add_edge("parse", "evaluate")
    workflow.add_edge("evaluate", "synthesize")
    
    workflow.set_entry_point("parse")
    workflow.set_finish_point("synthesize")
    
    return workflow.compile()
