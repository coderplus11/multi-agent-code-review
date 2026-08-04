"""Security agent: audits the diff for common vulnerability patterns."""

from langchain_core.messages import HumanMessage, SystemMessage

from src.llm import get_llm, invoke_with_retry
from src.logger import get_logger
from src.state import AgentState

_log = get_logger("security")

_SYSTEM_PROMPT = """You are a Security Reviewer agent specializing in vulnerability detection.

Analyze the provided code diff for:
- Injection risks (SQL, command, template, LDAP, etc.)
- Hardcoded secrets, API keys, or credentials
- Missing input validation/sanitization
- Broken authentication or authorization checks
- Insecure deserialization
- Sensitive data exposure (logging secrets, plaintext storage)
- Unsafe use of eval/exec or dynamic code execution
- Path traversal or unsafe file handling

Focus ONLY on security. Do not comment on style or general bugs.

Format your output as a numbered list, each item with:
- Vulnerability description and severity (LOW/MEDIUM/HIGH/CRITICAL)
- The problematic code snippet
- Suggested fix

If no issues are found, respond with:
"No security issues detected." """


def analyze_security(state: AgentState) -> dict:
    """Review the diff for security vulnerabilities."""
    _log.info("Auditing for security issues...")

    llm = get_llm()  # instantiated here, not at module import time
    response = invoke_with_retry(llm, [
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(content=f"Code diff to review:\n```\n{state.get('diff', '')}\n```"),
    ])

    return {"security_issues": [response.content]}
