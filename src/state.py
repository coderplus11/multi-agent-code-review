from typing import Any, Dict, List, Optional, TypedDict


class AgentState(TypedDict, total=False):
    """Shared state passed between every node in the review graph.

    Populated in src/main.py, read/written by src/agents/*.py and
    src/agents/orchestrator.py.
    """

    pr_number: Optional[int]
    pr_title: str
    diff: str
    files_changed: List[str]
    other_open_prs: List[Dict[str, Any]]

    security_issues: List[str]
    bug_issues: List[str]
    quality_issues: List[str]
    coverage_issues: List[str]
    cross_pr_issues: List[str]

    summary: str


# Export aliases so graph.py and all agents can import under whichever name
# they expect.
State = AgentState
ReviewState = AgentState
