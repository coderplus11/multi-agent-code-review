from typing import TypedDict, List, Dict, Any, Optional

class State(TypedDict):
    pr_number: Optional[int]
    pr_title: Optional[str]
    diff: str
    files_changed: List[str]
    
    # Context of other active PRs
    other_open_prs: List[Dict[str, Any]]
    
    # Agent Results
    security_issues: List[str]
    bug_issues: List[str]
    quality_issues: List[str]
    coverage_issues: List[str]
    cross_pr_issues: List[str]
    
    summary: str