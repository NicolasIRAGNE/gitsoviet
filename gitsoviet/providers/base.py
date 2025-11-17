from __future__ import annotations

from pathlib import Path
from typing import Protocol


class ImageProvider(Protocol):
    """Protocol that every provider must implement."""

    def generate(self, prompt: str, api_key: str, *, output_path: Path, language: str) -> Path:
        """Generate an image for the provided prompt and return output path."""
