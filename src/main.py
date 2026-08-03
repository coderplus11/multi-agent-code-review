import os
from github import Github
from src.graph import create_review_graph
from src.state import State

def fetch_other_open_prs(repo_name: str, current_pr_num: int = None) -> list:
    token = os.getenv("GITHUB_TOKEN")
    if not token or not repo_name:
        # Generic mock data for offline/local testing
        return [
            {
                "number": 12,
                "title": "Refactor Authentication Flow",
                "author": "developer_1",
                "files_changed": ["src/agents/security.py", "src/main.py"],
                "diff": "...sample diff..."
            }
        ]

    g = Github(token)
    repo = g.get_repo(repo_name)
    open_prs = repo.get_pulls(state='open')

    other_prs = []
    for pr in open_prs:
        if current_pr_num and pr.number == current_pr_num:
            continue
            
        other_prs.append({
            "number": pr.number,
            "title": pr.title,
            "author": pr.user.login,
            "files_changed": [f.filename for f in pr.get_files()],
            "diff": ""
        })

    return other_prs

def main():
    repo_name = os.getenv("GITHUB_REPOSITORY", "")
    current_pr = int(os.getenv("PR_NUMBER", "0")) or None

    initial_state: State = {
        "pr_number": current_pr,
        "pr_title": "Add Gemini Multi-Agent System",
        "diff": "+ def test(): pass",
        "files_changed": ["src/main.py", "src/state.py"],
        "other_open_prs": fetch_other_open_prs(repo_name, current_pr),
        "security_issues": [],
        "bug_issues": [],
        "quality_issues": [],
        "coverage_issues": [],
        "cross_pr_issues": [],
        "summary": ""
    }

    graph = create_review_graph()
    final_state = graph.invoke(initial_state)

    print(final_state["summary"])

if __name__ == "__main__":
    main()
