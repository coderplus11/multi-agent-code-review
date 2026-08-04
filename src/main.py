import os

from github import Github

from src.chunker import prepare_diff
from src.graph import create_review_graph
from src.logger import get_logger
from src.state import State

_log = get_logger("main")


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
                "diff": "...sample diff...",
            }
        ]

    g = Github(token)
    repo = g.get_repo(repo_name)
    open_prs = repo.get_pulls(state="open")

    other_prs = []
    for pr in open_prs:
        if current_pr_num and pr.number == current_pr_num:
            continue

        other_prs.append({
            "number": pr.number,
            "title": pr.title,
            "author": pr.user.login,
            "files_changed": [f.filename for f in pr.get_files()],
            "diff": "",
        })

    return other_prs


def fetch_pr_diff(repo_name: str, pr_number: int) -> tuple[str, list[str], str]:
    """Fetch the unified diff, changed files, and title for a real PR via the GitHub API.

    Returns (diff, files_changed, pr_title). Falls back to an empty diff if the
    token/repo/PR number aren't available (e.g. local/offline testing).
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token or not repo_name or not pr_number:
        return "", [], ""

    g = Github(token)
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)

    diff_parts = []
    files_changed = []
    for f in pr.get_files():
        files_changed.append(f.filename)
        patch = f.patch or ""
        diff_parts.append(f"diff --git a/{f.filename} b/{f.filename}\n{patch}")

    return "\n".join(diff_parts), files_changed, pr.title


def run_review(diff: str, files_changed: list[str], pr_number: int = None, pr_title: str = "") -> str:
    """Run the full multi-agent review pipeline on a given diff and return the summary.

    Public entry point used by src/cli.py, evals/run_eval.py, and code_review/__init__.py.
    """
    repo_name = os.getenv("GITHUB_REPOSITORY", "")
    safe_diff = prepare_diff(diff)

    initial_state: State = {
        "pr_number": pr_number,
        "pr_title": pr_title,
        "diff": safe_diff,
        "files_changed": files_changed,
        "other_open_prs": fetch_other_open_prs(repo_name, pr_number),
        "security_issues": [],
        "bug_issues": [],
        "quality_issues": [],
        "coverage_issues": [],
        "cross_pr_issues": [],
        "summary": "",
    }

    graph = create_review_graph()
    final_state = graph.invoke(initial_state)

    return final_state["summary"]


def main():
    """Entry point used by the GitHub Actions workflow."""
    repo_name = os.getenv("GITHUB_REPOSITORY", "")
    current_pr = int(os.getenv("PR_NUMBER", "0")) or None

    diff, files_changed, pr_title = "", [], "Add Gemini Multi-Agent System"
    if current_pr:
        diff, files_changed, fetched_title = fetch_pr_diff(repo_name, current_pr)
        pr_title = fetched_title or pr_title

    if not diff:
        # Fallback for local/manual runs with no real PR context
        diff = "+ def test(): pass"
        files_changed = ["src/main.py", "src/state.py"]

    summary = run_review(diff, files_changed, pr_number=current_pr, pr_title=pr_title)
    print(summary)


if __name__ == "__main__":
    main()
