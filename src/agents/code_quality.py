"""Code Quality agent: reviews readability, style, and maintainability."""

from langchain_core.messages import SystemMessage, HumanMessage

from src.llm import get_llm, invoke_with_retry
from src.logger import get_logger
from src.state import AgentState

_log = get_logger("code_quality")

_SYSTEM_PROMPT = """You are a Code Quality agent specializing in maintainability and readability.

Analyze the provided code diff for:
- Poor naming (cryptic variable/function names, misleading identifiers)
- Functions that are too long or do too many things (violate SRP)
- Code duplication (copy-pasted blocks that should be abstracted)
- Magic numbers or unexplained constants
- Deeply nested logic that should be flattened or extracted
- Dead code (unreachable code, unused variables/imports)
- Missing or misleading comments on complex logic
- Violation of language-specific style conventions (PEP 8 for Python, etc.)
- Overly complex expressions that could be simplified

Focus ONLY on quality, readability, and maintainability. Do not comment on bugs or security.

Format your output as a numbered list, each item with:
- Issue description
- The problematic code snippet
- Suggested improvement

If the code is clean and well-written, respond with:
"No code quality issues detected." """


def analyze_quality(state: AgentState) -> dict:
    """Review the diff for code quality and style issues."""
    _log.info("Checking readability and style...")

    llm = get_llm()  # instantiated here, not at module import time
    response = invoke_with_retry(llm, [
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(content=f"Code diff to review:\n```\n{state.get('diff', '')}\n```"),
    ])

    return {"quality_issues": [response.content]}





