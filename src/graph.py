from langgraph.graph import StateGraph, END
from src.state import State
from src.agents.security import analyze_security
from src.agents.bug_detector import detect_bugs
from src.agents.code_quality import analyze_quality
from src.agents.test_coverage import analyze_coverage
from src.agents.cross_pr_detector import detect_cross_pr_issues
from src.agents.orchestrator import format_final_summary

def create_review_graph():
    workflow = StateGraph(State)

    # Register Nodes
    workflow.add_node("security_agent", analyze_security)
    workflow.add_node("bug_agent", detect_bugs)
    workflow.add_node("quality_agent", analyze_quality)
    workflow.add_node("coverage_agent", analyze_coverage)
    workflow.add_node("cross_pr_agent", detect_cross_pr_issues)
    workflow.add_node("summarizer", format_final_summary)

    # Execution path
    workflow.set_entry_point("security_agent")
    workflow.add_edge("security_agent", "bug_agent")
    workflow.add_edge("bug_agent", "quality_agent")
    workflow.add_edge("quality_agent", "coverage_agent")
    workflow.add_edge("coverage_agent", "cross_pr_agent")
    workflow.add_edge("cross_pr_agent", "summarizer")
    workflow.add_edge("summarizer", END)

    return workflow.compile()
