def generate_final_summary(cross_pr_result: str, agent_reviews: dict) -> str:
    """Combines agent outputs into Markdown formatted for GitHub PR comments."""
    summary_markdown = "## 🤖 AI Code Review Summary\n\n"
    
    summary_markdown += "### 🔀 Cross-PR Check\n"
    summary_markdown += f"{cross_pr_result}\n\n"
    summary_markdown += "---\n\n"
    
    summary_markdown += "### 🔍 Agent Suggestions\n\n"
    for agent_name, review in agent_reviews.items():
        summary_markdown += f"#### {agent_name.replace('_', ' ').title()}\n"
        summary_markdown += f"{review}\n\n"
        
    return summary_markdown