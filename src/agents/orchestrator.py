import json
import ast
import re
from typing import Dict, Any
from src.state import State

def extract_pure_text(data: Any) -> str:
    """Recursively unwraps strings, dicts, lists, and AIMessage objects into clean Markdown text."""
    if not data:
        return ""

    # If it's a dict or AIMessage object representation
    if isinstance(data, dict):
        if "text" in data:
            return extract_pure_text(data["text"])
        if "content" in data:
            return extract_pure_text(data["content"])
        return str(data)

    # If it's a list (e.g., [{'type': 'text', 'text': '...'}])
    if isinstance(data, list):
        extracted_chunks = [extract_pure_text(item) for item in data]
        return "\n\n".join(filter(None, extracted_chunks))

    # If it's a string representation of Python lists/dicts
    if isinstance(data, str):
        text_str = data.strip()
        
        # Unquote Python repr strings if present
        if (text_str.startswith("[") and text_str.endswith("]")) or (text_str.startswith("{") and text_str.endswith("}")):
            try:
                parsed = json.loads(text_str)
                return extract_pure_text(parsed)
            except Exception:
                try:
                    parsed = ast.literal_eval(text_str)
                    return extract_pure_text(parsed)
                except Exception:
                    pass
        return text_str

    return str(data)

def format_section(raw_content: Any) -> str:
    """Converts agent output into clean Markdown text."""
    clean_text = extract_pure_text(raw_content)
    
    if not clean_text or clean_text.strip() == "[]":
        return "No issues detected."

    # Remove lingering 1. prefixes created by list indexing wrappers if they exist
    clean_text = re.sub(r'^\d+\.\s*(?=\[\{)', '', clean_text)
    
    return clean_text.strip()

def orchestrate_review(state: State) -> Dict[str, Any]:
    return {}

def format_final_summary(state: State) -> Dict[str, str]:
    # Extract states
    cross_raw = state.get("cross_pr_review") or state.get("cross_pr_issues")
    sec_raw = state.get("security_issues") or state.get("security")
    bugs_raw = state.get("bug_issues") or state.get("bug_detector")
    qual_raw = state.get("quality_issues") or state.get("code_quality")
    cov_raw = state.get("coverage_issues") or state.get("test_coverage")

    # Format sections
    cross = format_section(cross_raw)
    if cross == "No issues detected." or not cross_raw:
        cross = (
            "No overlapping files found with other open PRs.\n\n"
            "**Merge conflict risk:** LOW\n\n"
            "**Developer overlap:** None\n\n"
            "**Recommendation:** Safe to merge after review."
        )

    sec = format_section(sec_raw)
    bugs = format_section(bugs_raw)
    qual = format_section(qual_raw)
    cov = format_section(cov_raw)

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