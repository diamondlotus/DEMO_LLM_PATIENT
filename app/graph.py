# app/graph.py
from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI
from app.agents import parser_agent, evaluator_agent, synthesizer_agent
from app.state import WorkflowState   # ✅ import đúng schema

llm = ChatOpenAI(model="gpt-4o-mini")

def build_graph():
    workflow = StateGraph(WorkflowState)   # ✅ dùng schema đã import

    parse = parser_agent(llm)
    evaluate = evaluator_agent(llm)
    synthesize = synthesizer_agent(llm)

    workflow.add_node("parse", lambda state: {"data": parse(state["note"])})
    workflow.add_node("evaluate", lambda state: {"validated_data": evaluate(state["data"])})
    workflow.add_node("synthesize", lambda state: {"report": synthesize(state["validated_data"])})

    workflow.add_edge("parse", "evaluate")
    workflow.add_edge("evaluate", "synthesize")

    workflow.set_entry_point("parse")
    workflow.set_finish_point("synthesize")

    return workflow.compile()

