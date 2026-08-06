import json
import ast

def clean_agent_output(raw_output) -> str:
    """Extracts human-readable text from LLM state returns (handles strings, lists, dicts)."""
    if not raw_output:
        return "No feedback provided."
    
    # Handle list of dicts/objects
    if isinstance(raw_output, list):
        extracted = []
        for item in raw_output:
            if isinstance(item, dict) and "text" in item:
                extracted.append(item["text"])
            elif isinstance(item, dict) and "content" in item:
                extracted.append(item["content"])
            else:
                extracted.append(str(item))
        return "\n\n".join(extracted)
    
    # Handle stringified lists/dicts
    if isinstance(raw_output, str):
        raw_str = raw_output.strip()
        if (raw_str.startswith("[") and raw_str.endswith("]")) or (raw_str.startswith("{") and raw_str.endswith("}")):
            try:
                parsed = json.loads(raw_str)
                return clean_agent_output(parsed)
            except Exception:
                try:
                    parsed = ast.literal_eval(raw_str)
                    return clean_agent_output(parsed)
                except Exception:
                    pass
        return raw_str

    return str(raw_output)


def format_concise_section(title: str, raw_content: str) -> str:
    """Ensures section feedback is formatted cleanly or defaults to a short success badge."""
    cleaned = clean_agent_output(raw_content)
    
    # Fallback check for empty responses or no issues detected
    if not cleaned or any(phrase in cleaned for phrase in ["No issues detected", "No security issues detected", "No feedback provided", "[]"]):
        return f"### {title}\n- ✅ No critical issues found.\n"
    
    return f"### {title}\n{cleaned.strip()}\n"


def generate_final_summary(cross_pr_result: str, agent_reviews: dict) -> str:
    """Combines agent outputs into a concise Markdown summary formatted for GitHub PR comments."""
    summary_markdown = "# 🤖 Multi-Agent Code Review Report\n\n"
    
    # 1. Cross-PR Section
    summary_markdown += "### 🔀 Cross-PR & Developer Overlap Analysis\n"
    clean_cross = clean_agent_output(cross_pr_result)
    
    if clean_cross == "None" or not clean_cross or "No issues detected" in clean_cross:
        clean_cross = (
            "No overlapping files found with other open PRs.\n\n"
            "**Merge conflict risk:** LOW\n\n"
            "**Developer overlap:** None\n\n"
            "**Recommendation:** Safe to merge after review."
        )
    
    summary_markdown += f"{clean_cross}\n\n---\n\n"
    
    # 2. Sub-agent Sections
    titles = {
        "security": "🛡️ Security Audit",
        "bug_detector": "🪲 Bug Detection",
        "code_quality": "🎨 Code Quality & Style",
        "test_coverage": "🧪 Test Coverage Analysis"
    }

    for key, title in titles.items():
        # Fallback check for alternative key names in state
        raw_content = agent_reviews.get(key) or agent_reviews.get(f"{key}_issues")
        summary_markdown += format_concise_section(title, raw_content) + "\n"
        
    return summary_markdown