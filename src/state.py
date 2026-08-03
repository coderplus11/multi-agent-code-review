# src/state.py
from typing import TypedDict, List, Dict, Any

class AgentState(TypedDict):
    # Your state keys (e.g., pr_details, reviews, etc.)
    ...

# Alias ReviewState to AgentState so any agent importing ReviewState works
ReviewState = AgentState