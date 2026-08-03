from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict, total=False):
    pr_details: Dict[str, Any]
    reviews: Dict[str, Any]
    messages: List[Any]

ReviewState = AgentState
