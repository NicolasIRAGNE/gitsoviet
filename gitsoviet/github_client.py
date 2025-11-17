from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests


@dataclass
class PullRequestInfo:
    number: int
    title: str
    body: str
    html_url: str
    head_sha: str


class GitHubClient:
    """Minimal GitHub API helper."""

    def __init__(self, token: Optional[str] = None, api_url: str = "https://api.github.com") -> None:
        self.api_url = api_url.rstrip("/")
        self.session = requests.Session()
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"
        self.session.headers["Accept"] = "application/vnd.github+json"
        self.session.headers["User-Agent"] = "gitsoviet/0.1"

    def _request(self, method: str, endpoint: str) -> Any:
        url = f"{self.api_url}{endpoint}"
        response = self.session.request(method, url, timeout=30)
        if response.status_code >= 400:
            raise RuntimeError(f"GitHub API error {response.status_code}: {response.text}")
        return response.json()

    def get_pull_request(self, repo: str, number: int) -> PullRequestInfo:
        data = self._request("GET", f"/repos/{repo}/pulls/{number}")
        return PullRequestInfo(
            number=data["number"],
            title=data.get("title", ""),
            body=data.get("body", ""),
            html_url=data.get("html_url", ""),
            head_sha=data.get("head", {}).get("sha", ""),
        )

    def get_pull_request_files(self, repo: str, number: int) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        page = 1
        while True:
            data = self._request("GET", f"/repos/{repo}/pulls/{number}/files?page={page}&per_page=100")
            if not data:
                break
            results.extend(data)
            page += 1
        return results
