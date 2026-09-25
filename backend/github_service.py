import re
import os
import requests
from typing import Dict, Any, Tuple

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

def parse_github_pr_url(url: str) -> Tuple[str, str, str]:
    """Parses owner, repo, pr_number from a GitHub PR URL."""
    pattern = r"github\.com/([^/]+)/([^/]+)/pull/(\d+)"
    match = re.search(pattern, url)
    if not match:
        raise ValueError("Invalid GitHub PR URL format. Expected: https://github.com/owner/repo/pull/123")
    return match.group(1), match.group(2), match.group(3)

def fetch_github_pr_files(pr_url: str) -> Tuple[Dict[str, str], Dict[str, Any]]:
    """Fetches files and metadata for a GitHub Pull Request."""
    owner, repo, pr_num = parse_github_pr_url(pr_url)
    
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    # 1. Fetch PR details
    pr_api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_num}"
    pr_resp = requests.get(pr_api_url, headers=headers, timeout=10)
    
    if pr_resp.status_code == 404:
        raise ValueError(f"GitHub PR not found: {owner}/{repo} #{pr_num}")
    elif pr_resp.status_code == 403:
        raise ValueError("GitHub API rate limit exceeded. Please configure GITHUB_TOKEN in .env or try again later.")
    elif pr_resp.status_code != 200:
        raise ValueError(f"Failed to fetch GitHub PR ({pr_resp.status_code}): {pr_resp.text}")

    pr_data = pr_resp.json()
    pr_meta = {
        "title": pr_data.get("title", f"PR #{pr_num}"),
        "author": pr_data.get("user", {}).get("login", "unknown"),
        "repo": f"{owner}/{repo}",
        "pr_number": pr_num,
        "url": pr_url,
        "branch": pr_data.get("head", {}).get("ref", "main")
    }

    # 2. Fetch PR files
    files_api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_num}/files"
    files_resp = requests.get(files_api_url, headers=headers, timeout=10)
    
    if files_resp.status_code != 200:
        raise ValueError(f"Failed to fetch PR changed files: {files_resp.text}")

    files_list = files_resp.json()
    repo_files = {}

    for f_info in files_list:
        fname = f_info.get("filename", "")
        # Filter for Python files
        if fname.endswith(".py"):
            raw_url = f_info.get("raw_url")
            if raw_url:
                content_resp = requests.get(raw_url, headers=headers, timeout=10)
                if content_resp.status_code == 200:
                    repo_files[fname] = content_resp.text

    if not repo_files:
        raise ValueError(f"No Python (.py) files found in PR #{pr_num}. DevPulse AI currently audits Python PRs.")

    return repo_files, pr_meta
