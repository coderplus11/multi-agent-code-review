import json
import ast
from typing import Dict, Any
from src.state import State

def extract_text(item: Any) -> str:
    """Helper to pull clean string text out of raw LLM return objects."""
    if isinstance(item, dict):
        if "text" in item:
            return item["text"]
        return str(item)
    return str(item)

def format_issue_block(raw_content: Any) -> str:
    """Parses raw agent output and formats it into clean GitHub Markdown."""
    if not raw_content:
        return "No issues detected."

    # Parse JSON or literal strings if necessary
    parsed_data = raw_content
    if isinstance(raw_content, str):
        content_str = raw_content.strip()
        if (content_str.startswith("[") and content_str.endswith("]")) or (content_str.startswith("{") and content_str.endswith("}")):
            try:
                parsed_data = json.loads(content_str)
            except Exception:
                try:
                    parsed_data = ast.literal_eval(content_str)
                except Exception:
                    parsed_data = content_str

    # Process list of items
    if isinstance(parsed_data, list):
        cleaned_items = []
        for index, entry in enumerate(parsed_data, 1):
            text_content = extract_text(entry)
            cleaned_items.append(f"**{index}.** {text_content}")
        return "\n\n".join(cleaned_items)
    
    return str(parsed_data)

def orchestrate_review(state: State) -> Dict[str, Any]:
    return {}

def format_final_summary(state: State) -> Dict[str, str]:
    # Extract states
    cross_raw = state.get("cross_pr_review") or state.get("cross_pr_issues")
    sec_raw = state.get("security_issues") or state.get("security")
    bugs_raw = state.get("bug_issues") or state.get("bug_detector")
    qual_raw = state.get("quality_issues") or state.get("code_quality")
    cov_raw = state.get("coverage_issues") or state.get("test_coverage")

    # Format Cross-PR block
    cross = format_issue_block(cross_raw)
    if cross == "No issues detected." or not cross_raw:
        cross = (
            "No overlapping files found with other open PRs.\n\n"
            "**Merge conflict risk:** LOW\n\n"
            "**Developer overlap:** None\n\n"
            "**Recommendation:** Safe to merge after review."
        )

    sec = format_issue_block(sec_raw)
    bugs = format_issue_block(bugs_raw)
    qual = format_issue_block(qual_raw)
    cov = format_issue_block(cov_raw)

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