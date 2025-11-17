from __future__ import annotations

import base64
from pathlib import Path
from typing import Optional

from openai import OpenAI

from .base import ImageProvider


class OpenAIProvider(ImageProvider):
    """OpenAI image generation API (DALL-E/GPT-Image)."""

    def __init__(self, *, model: str = "gpt-image-1", size: Optional[str] = None) -> None:
        self.model = model
        self.size = size or "1024x1536"

    def generate(self, prompt: str, api_key: str, *, output_path: Path, language: str) -> Path:
        client = OpenAI(api_key=api_key)
        response = client.images.generate(model=self.model, prompt=prompt, size=self.size)
        try:
            raw = response.data[0].b64_json
        except (KeyError, IndexError) as exc:  # pragma: no cover - defensive
            raise RuntimeError(f"Unexpected OpenAI response: {response}") from exc
        image_bytes = base64.b64decode(raw)
        output_path.write_bytes(image_bytes)
        return output_path
