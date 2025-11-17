from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar


@dataclass(slots=True)
class PosterRequest:
    repo_name: str
    pr_title: str
    pr_description: str
    pr_author: str
    diff: str
    format: str = "poster"
    style: str = "soviet"
    language: str = "English"
    additional_prompt: str = ""
    format_key: str = field(init=False)
    style_key: str = field(init=False)
    _format_config: dict[str, str] = field(init=False, repr=False)

    FORMATS: ClassVar[dict[str, dict[str, str]]] = {
        "poster": {"label": "Poster", "size": "1024x1536"},
        "mural": {"label": "Mural", "size": "1536x1024"},
    }
    STYLES: ClassVar[dict[str, str]] = {
        "soviet": "Soviet",
        "dprk": "DPRK",
        "cuban": "Cuban",
        "capitalist": "Capitalist",
        "royalist": "Royalist",
    }

    def __post_init__(self) -> None:
        self.format_key = self._normalize(self.format)
        self.style_key = self._normalize(self.style)
        if self.format_key not in self.FORMATS:
            raise ValueError(f"Unsupported format '{self.format}'. Available: {', '.join(sorted(self.FORMATS))}")
        if self.style_key not in self.STYLES:
            raise ValueError(f"Unsupported style '{self.style}'. Available: {', '.join(sorted(self.STYLES))}")
        self._format_config = self.FORMATS[self.format_key]

    @property
    def format_label(self) -> str:
        return self._format_config["label"]

    @property
    def style_label(self) -> str:
        return self.STYLES[self.style_key]

    @property
    def image_size(self) -> str:
        return self._format_config["size"]

    @staticmethod
    def _normalize(value: str) -> str:
        return value.strip().lower().replace(" ", "_")

