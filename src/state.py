# src/state.py

from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    # your state definitions...
    messages: List[Any]
    pr_details: Dict[str, Any]
    reviews: Dict[str, Any]

# Add this alias so both 'AgentState' and 'ReviewState' imports work seamlessly
ReviewState = AgentState