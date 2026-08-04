"""Bug Detector agent: finds logic errors, edge cases, and runtime risks."""

from langchain_core.messages import HumanMessage, SystemMessage

from src.llm import get_llm, invoke_with_retry
from src.logger import get_logger
from src.state import AgentState

_log = get_logger("bug_detector")

_SYSTEM_PROMPT = """You are a Bug Detector agent specializing in logic errors and runtime risks.

Analyze the provided code diff for:
- Off-by-one errors and incorrect loop/boundary conditions
- Null/None/undefined handling issues
- Incorrect operator usage (e.g. `=` vs `==`, wrong comparison direction)
- Unhandled exceptions or error paths
- Race conditions or state mutation bugs
- Incorrect assumptions about input types or shapes
- Logic that contradicts the apparent intent of the surrounding code

Focus ONLY on functional correctness. Do not comment on style or security.

Format your output as a numbered list, each item with:
- Issue description
- The problematic code snippet
- Suggested fix

If no bugs are found, respond with:
"No bugs detected." """


def detect_bugs(state: AgentState) -> dict:
    """Review the diff for logic bugs and runtime risks."""
    _log.info("Scanning for logic bugs...")

    llm = get_llm()  # instantiated here, not at module import time
    response = invoke_with_retry(llm, [
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(content=f"Code diff to review:\n```\n{state.get('diff', '')}\n```"),
    ])

    return {"bug_issues": [response.content]}
