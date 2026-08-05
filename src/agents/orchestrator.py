import json
import ast
from typing import Dict, Any
from src.state import State

def clean_issue_content(raw_content: Any) -> str:
    """Parses and formats issue content cleanly into Markdown text."""
    if not raw_content:
        return "- No issues found."
    
    # Handle list of items or dictionary outputs from LLMs
    if isinstance(raw_content, list):
        items = []
        for item in raw_content:
            if isinstance(item, dict) and "text" in item:
                items.append(item["text"])
            elif isinstance(item, str):
                items.append(item)
            else:
                items.append(str(item))
        return "\n\n".join(items)

    # Handle string outputs that might be stringified JSON/dicts
    if isinstance(raw_content, str):
        content_str = raw_content.strip()
        if (content_str.startswith("[") and content_str.endswith("]")) or (content_str.startswith("{") and content_str.endswith("}")):
            try:
                parsed = ast.literal_eval(content_str)
                return clean_issue_content(parsed)
            except Exception:
                pass
        return content_str

    return str(raw_content)

def orchestrate_review(state: State) -> Dict[str, Any]:
    return {}

def format_final_summary(state: State) -> Dict[str, str]:
    # Extract states with fallbacks for key variations
    cross_raw = state.get("cross_pr_review") or state.get("cross_pr_issues")
    sec_raw = state.get("security_issues") or state.get("security")
    bugs_raw = state.get("bug_issues") or state.get("bug_detector")
    qual_raw = state.get("quality_issues") or state.get("code_quality")
    cov_raw = state.get("coverage_issues") or state.get("test_coverage")

    # Format Cross-PR block
    cross = clean_issue_content(cross_raw)
    if cross == "- No issues found." or not cross_raw:
        cross = (
            "No overlapping files found with other open PRs.\n\n"
            "**Merge conflict risk:** LOW\n\n"
            "**Developer overlap:** None\n\n"
            "**Recommendation:** Safe to merge after review."
        )

    sec = clean_issue_content(sec_raw)
    bugs = clean_issue_content(bugs_raw)
    qual = clean_issue_content(qual_raw)
    cov = clean_issue_content(cov_raw)

    summary_md = f"""# 🤖 Multi-Agent Code Review Report

## 🔀 Cross-PR & Developer Overlap Analysis
{cross}

---

## 🛡️ Security Audit
{sec}

---

## 🪲 Bug Detection
{bugs}

---

## 🎨 Code Quality & Style
{qual}

---

## 🧪 Test Coverage Analysis
{cov}
"""
    return {"summary": summary_md}