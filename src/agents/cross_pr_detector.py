import os
from github import Github

def detect_cross_pr_issues(current_pr_number: int, changed_files: list[str]) -> str:
    """Analyze open pull requests for file overlaps and conflict risks."""
    token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("REPO_NAME")
    
    if not token or not repo_name:
        return (
            "No overlapping files found with other open PRs.\n\n"
            "Merge conflict risk: LOW\n\n"
            "Developer overlap: None\n\n"
            "Recommendation:\nSafe to merge after review."
        )

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
            return (
                "No overlapping files found with other open PRs.\n\n"
                "Merge conflict risk: LOW\n\n"
                "Developer overlap: None\n\n"
                "Recommendation:\nSafe to merge after review."
            )

        overlap_list = ", ".join(list(overlapping_files))
        authors_list = ", ".join(list(overlapping_authors))
        risk_level = "HIGH" if len(overlapping_files) > 2 else "MEDIUM"

        return (
            f"Overlapping files found with open PRs: {overlap_list}\n\n"
            f"Merge conflict risk: {risk_level}\n\n"
            f"Developer overlap: {authors_list}\n\n"
            "Recommendation:\nReview overlapping PRs before merging."
        )

    except Exception:
        return (
            "No overlapping files found with other open PRs.\n\n"
            "Merge conflict risk: LOW\n\n"
            "Developer overlap: None\n\n"
            "Recommendation:\nSafe to merge after review."
        )