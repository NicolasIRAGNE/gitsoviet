from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

from jinja2 import Template

ROOT = Path(__file__).resolve().parent

PROMPT_TEMPLATE = Template(
    """
{{ format_prompt }}

{{ style_prompt }}

Slogan language: {{ language }}.

Pull request context:
- Title: {{ title }}
- Description: {{ body }}
- Changed files:
{%- for file in changed_files %}
  - {{ file }}
{%- endfor %}

Diff summary:
{{ diff }}

Additional creative direction:
{{ guidance }}
"""
)


@dataclass
class PromptComponents:
    format_prompt: str
    style_prompt: str
    title: str
    body: str
    changed_files: List[str]
    diff: str
    guidance: str
    language: str


class PromptBuilder:
    def __init__(self, base_path: Path | None = None) -> None:
        self.base_path = base_path or ROOT

    def load_fragment(self, folder: str, name: str) -> str:
        path = self.base_path / folder / f"{name.lower()}.txt"
        if not path.exists():
            available = ", ".join(sorted(p.stem for p in (self.base_path / folder).glob("*.txt")))
            raise ValueError(f"Unknown {folder[:-1]} '{name}'. Available: {available}")
        return path.read_text(encoding="utf-8").strip()

    def build(self, *, format_name: str, style_name: str, title: str, body: str, changed_files: Iterable[str], diff: str, guidance: str, language: str) -> str:
        components = PromptComponents(
            format_prompt=self.load_fragment("formats", format_name),
            style_prompt=self.load_fragment("styles", style_name),
            title=title.strip(),
            body=body.strip(),
            changed_files=list(changed_files),
            diff=diff.strip(),
            guidance=guidance.strip(),
            language=language.strip() or "English",
        )
        return PROMPT_TEMPLATE.render(**components.__dict__)
