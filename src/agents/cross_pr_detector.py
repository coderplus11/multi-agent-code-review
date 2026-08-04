from typing import List, Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from src.llm import get_llm
from src.state import State

SYSTEM_PROMPT = """You are a Senior Software Architect reviewing a Pull Request.
Your job is to compare the current PR's diff against OTHER currently open PRs in the repository.

Look for two main types of issues:
1. Direct File/Line Collisions: Multiple PRs modifying the same functions or files concurrently.
2. Breaking Logical Dependencies: e.g., Current PR relies on a function signature that another open PR is modifying or deleting.

Be concise. If there are no cross-PR conflicts or risks, explicitly state 'NO_CONFLICTS'.
"""

def detect_cross_pr_issues(state: State) -> Dict[str, List[str]]:
    diff = state.get("diff", "")
    files_changed = state.get("files_changed", [])
    other_prs = state.get("other_open_prs", [])

    if not other_prs:
        return {"cross_pr_issues": ["No other open PRs detected to check against."]}

    # Step 1: Programmatic check for overlapping files
    overlapping_prs = []
    for pr in other_prs:
        common_files = set(files_changed).intersection(set(pr.get("files_changed", [])))
        if common_files:
            overlapping_prs.append({
                "pr_number": pr.get("number"),
                "title": pr.get("title"),
                "author": pr.get("author", "contributor"),
                "overlapping_files": list(common_files),
                "diff": pr.get("diff", "")
            })

    if not overlapping_prs:
        return {"cross_pr_issues": ["No overlapping files found with other open PRs."]}

    # Step 2: LLM analysis using Gemini
    try:
        llm = get_llm()  # instantiated here, not at module import time
    except ValueError:
        # No API key available -- fall back to the programmatic collision report
        findings = [
            f"[Warning] File Collision: PR #{p['pr_number']} ('{p['title']}') by @{p['author']} "
            f"also touches: {', '.join(p['overlapping_files'])}"
            for p in overlapping_prs
        ]
        return {"cross_pr_issues": findings}

    prompt = f"""Current PR Diff:
{diff}

Other Overlapping Open PRs:
{overlapping_prs}

Analyze if these concurrent changes will cause merge conflicts or runtime logic failures.
"""

    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=prompt)
    ])

    result_text = response.content.strip()

    if result_text == "NO_CONFLICTS":
        return {"cross_pr_issues": ["Overlapping files detected, but no logical conflicts found."]}

    return {"cross_pr_issues": [result_text]}
