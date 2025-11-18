from __future__ import annotations

from dataclasses import dataclass, asdict
from importlib import resources
from pathlib import Path

from jinja2 import Environment


@dataclass(slots=True)
class PromptContext:
    repo_name: str
    pr_title: str
    pr_description: str
    pr_author: str
    diff: str
    format_label: str
    style_label: str
    format_prompt: str
    style_prompt: str
    language: str
    additional_prompt: str


class PromptBuilder:
    """Loads prompt templates and produces the final message for providers."""

    def __init__(self, base_path: str | Path | None = None) -> None:
        self.base_path = Path(base_path) if base_path else None
        self.env = Environment(autoescape=False, trim_blocks=True, lstrip_blocks=True)

    def build(self, *, request: "PosterRequest") -> str:  # pragma: no cover - typed at runtime
        base_template = self._read_text("base_prompt.j2")
        format_prompt = self._read_text(Path("formats") / f"{request.format_key}.txt")
        style_prompt = self._read_text(Path("styles") / f"{request.style_key}.txt")
        template = self.env.from_string(base_template)
        context = PromptContext(
            repo_name=request.repo_name,
            pr_title=request.pr_title,
            pr_description=request.pr_description,
            pr_author=request.pr_author,
            diff=request.diff,
            format_label=request.format_label,
            style_label=request.style_label,
            format_prompt=format_prompt.strip(),
            style_prompt=style_prompt.strip(),
            language=request.language,
            additional_prompt=request.additional_prompt,
        )
        return template.render(**asdict(context))

    def _read_text(self, relative_path: str | Path) -> str:
        if self.base_path:
            target = (self.base_path / relative_path).resolve()
            return target.read_text(encoding="utf-8")
        package_root = resources.files("gitsoviet") / "templates" / relative_path
        return package_root.read_text(encoding="utf-8")


# Imported lazily to avoid circular import during typing.
from .request import PosterRequest  # noqa: E402  # isort:skip


