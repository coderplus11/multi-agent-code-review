import json
import ast

def clean_agent_output(raw_output) -> str:
    """Extracts human-readable text from LLM state returns (handles strings, lists, dicts)."""
    if not raw_output:
        return "No feedback provided."
    
    # If the output is a list/dict object
    if isinstance(raw_output, list):
        extracted = []
        for item in raw_output:
            if isinstance(item, dict) and "text" in item:
                extracted.append(item["text"])
            else:
                extracted.append(str(item))
        return "\n\n".join(extracted)
    
    # If it is a string representing a list/dict, parse it
    if isinstance(raw_output, str):
        raw_str = raw_output.strip()
        if (raw_str.startswith("[") and raw_str.endswith("]")) or (raw_str.startswith("{") and raw_str.endswith("}")):
            try:
                parsed = ast.literal_eval(raw_str)
                return clean_agent_output(parsed)
            except Exception:
                pass
        return raw_str

    return str(raw_output)


def generate_final_summary(cross_pr_result: str, agent_reviews: dict) -> str:
    """Combines agent outputs into clean Markdown formatted for GitHub PR comments."""
    summary_markdown = "## 🤖 Multi-Agent Code Review Report\n\n"
    
    # Cross-PR Section
    summary_markdown += "### 🔀 Cross-PR & Developer Overlap Analysis\n"
    clean_cross = clean_agent_output(cross_pr_result)
    if clean_cross == "None" or not clean_cross:
        clean_cross = (
            "No overlapping files found with other open PRs.\n\n"
            "Merge conflict risk: LOW\n\n"
            "Developer overlap: None\n\n"
            "**Recommendation:** Safe to merge after review."
        )
    summary_markdown += f"{clean_cross}\n\n"
    summary_markdown += "---\n\n"
    
    # Sub-agent sections
    titles = {
        "security": "🛡️ Security Audit",
        "bug_detector": "🪲 Bug Detection",
        "code_quality": "🎨 Code Quality & Style",
        "test_coverage": "🧪 Test Coverage Analysis"
    }

    for key, title in titles.items():
        if key in agent_reviews:
            summary_markdown += f"### {title}\n"
            summary_markdown += f"{clean_agent_output(agent_reviews[key])}\n\n"
        
    return summary_markdown