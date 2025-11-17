from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass
class PRData:
    title: str
    body: str
    changed_files: List[str]
    diff: str


def load_pr_from_event(event: Any) -> Optional[PRData]:
    pull_request = event.get("pull_request") if isinstance(event, dict) else None
    if not pull_request:
        return None
    title = pull_request.get("title", "")
    body = pull_request.get("body", "")

    changed_files = []
    if "gitsoviet" in pull_request:
        details = pull_request["gitsoviet"]
        changed_files = details.get("changed_files", []) or []
        diff = details.get("diff", "")
    else:
        diff = ""

    return PRData(title=title, body=body, changed_files=changed_files, diff=diff)
