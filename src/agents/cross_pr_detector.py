import os
from github import Github

def detect_cross_pr_issues(state: dict) -> dict:
    """Analyze open pull requests for file overlaps and conflict risks."""
    token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("REPO_NAME")
    
    current_pr_number = state.get("pr_number") or os.getenv("PR_NUMBER", 0)
    changed_files = state.get("files_changed", [])

    default_result = (
        "No overlapping files found with other open PRs.\n\n"
        "Merge conflict risk: LOW\n\n"
        "Developer overlap: None\n\n"
        "Recommendation:\nSafe to merge after review."
    )

    if not token or not repo_name or not changed_files:
        return {"cross_pr_review": default_result}

    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        open_prs = repo.get_pulls(state='open')

        overlapping_files = set()
        overlapping_authors = set()

        for pr in open_prs:
            if pr.number == int(current_pr_number):
                continue

            pr_files = [f.filename for f in pr.get_files()]
            overlap = set(changed_files).intersection(set(pr_files))

            if overlap:
                overlapping_files.update(overlap)
                overlapping_authors.add(pr.user.login)

        if not overlapping_files:
            return {"cross_pr_review": default_result}

        overlap_list = ", ".join(list(overlapping_files))
        authors_list = ", ".join(list(overlapping_authors))
        risk_level = "HIGH" if len(overlapping_files) > 2 else "MEDIUM"

        result_text = (
            f"Overlapping files found with open PRs: {overlap_list}\n\n"
            f"Merge conflict risk: {risk_level}\n\n"
            f"Developer overlap: {authors_list}\n\n"
            "Recommendation:\nReview overlapping PRs before merging."
        )
        return {"cross_pr_review": result_text}

    except Exception:
        return {"cross_pr_review": default_result}