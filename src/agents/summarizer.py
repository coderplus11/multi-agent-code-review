"""Summarizer agent: merges all specialist reports into one prioritized review."""

from langchain_core.messages import SystemMessage, HumanMessage

from src.llm import get_llm
from src.logger import get_logger
from src.state import AgentState

_log = get_logger("summarizer")

_SYSTEM_PROMPT = """You are a Code Review Summarizer. Your job is to synthesize reports from multiple specialist agents into a single, clean, developer-friendly review.

You will receive outputs from up to four specialist agents:
1. Logic & Bug Detector
2. Security Reviewer
3. Code Quality Reviewer
4. Test Coverage Reviewer

Your output must follow this structure:

---
## Code Review Summary

### Critical Issues  (must fix before merge)
<List only CRITICAL/HIGH severity bugs and security vulnerabilities>

### Suggestions  (should fix, improves quality)
<Medium severity issues: logic concerns, quality problems, missing tests>

### Nitpicks  (optional, minor improvements)
<Low severity style notes, minor naming issues, optional refactors>

### Verdict
<One of: APPROVE | REQUEST CHANGES | NEEDS DISCUSSION>
<One sentence rationale>
---

Rules:
- Merge duplicate findings across agents into a single item.
- Do not repeat the same issue multiple times.
- Use concise, actionable language â€” write for the PR author.
- If a section has no items, write "None."
- Always include the Verdict.

Contradiction resolution:
- If agents DISAGREE on severity (e.g., Bug Detector calls something critical but Quality agent treats it as a style nit), always escalate to the HIGHER severity and note the disagreement inline: "(severity disputed â€” escalated to higher)".
- If agents give CONFLICTING refactor advice for the same code (e.g., one says extract a helper, another says inline it), present both options with a one-line tradeoff and let the author decide.
- If one agent flags a pattern as a bug but another implicitly accepts it, add it to Suggestions with a note: "(correctness uncertain â€” recommend team discussion)"."""


_REPORT_SECTIONS = [
    ("bug_issues", "### Logic & Bug Report"),
    ("security_issues", "### Security Report"),
    ("quality_issues", "### Code Quality Report"),
    ("coverage_issues", "### Test Coverage Report"),
]


def _build_combined_report(state: AgentState) -> str:
    """Concatenate all non-empty specialist reports into one string."""
    sections = [
        f"{header}\n" + "\n".join(state[key])
        for key, header in _REPORT_SECTIONS
        if state.get(key)
    ]
    return "\n\n".join(sections) if sections else "No specialist reports were generated."


def summarizer_node(state: AgentState) -> dict:
    """Synthesize all specialist reports into a single prioritized review."""
    _log.info("Compiling final review...")

    combined = _build_combined_report(state)

    llm = get_llm()  # instantiated here, not at module import time
    response = llm.invoke([
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(content=(
            f"Specialist agent reports:\n\n{combined}\n\n"
            f"Please synthesize these into a final code review."
        )),
    ])

    return {"final_review": response.content}





