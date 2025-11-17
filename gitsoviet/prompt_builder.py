from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

from jinja2 import Environment, FileSystemLoader, StrictUndefined


@dataclass
class PromptContext:
    format_name: str
    style_name: str
    language: str
    pr_title: str
    pr_body: str
    diff_summary: str
    extra_guidance: str


class PromptBuilder:
    def __init__(self, *, data_dir: Path, templates_dir: Path) -> None:
        self.data_dir = data_dir
        self.templates_dir = templates_dir
        self.env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
            undefined=StrictUndefined,
        )

    def _load_text(self, folder: str, name: str) -> str:
        candidate = self.data_dir / folder / f"{name.lower()}.txt"
        if not candidate.exists():
            available = sorted(p.stem for p in (self.data_dir / folder).glob("*.txt"))
            raise ValueError(f"Unknown {folder[:-1]} '{name}'. Available: {', '.join(available)}")
        return candidate.read_text(encoding="utf-8").strip()

    def build(self, ctx: PromptContext) -> str:
        template = self.env.get_template("prompt.j2")
        format_prompt = self._load_text("formats", ctx.format_name)
        style_prompt = self._load_text("styles", ctx.style_name)
        return template.render(
            format_prompt=format_prompt,
            style_prompt=style_prompt,
            language=ctx.language,
            pr_title=ctx.pr_title,
            pr_body=ctx.pr_body,
            diff_summary=ctx.diff_summary,
            extra_guidance=ctx.extra_guidance,
        )


def summarize_files(files: Iterable[dict], *, max_chars: int = 3500) -> str:
    lines: List[str] = []
    for file in files:
        header = f"* {file.get('filename')} (+{file.get('additions', 0)}/-{file.get('deletions', 0)})"
        lines.append(header)
        patch = file.get("patch") or ""
        if patch:
            snippet = "\n".join(line[:160] for line in patch.splitlines()[:10])
            lines.append(f"  Summary:\n    {snippet.replace('\n', '\n    ')}")
        if sum(len(line) for line in lines) > max_chars:
            break
    summary = "\n".join(lines)
    if len(summary) > max_chars:
        summary = summary[: max_chars - 3] + "..."
    return summary
