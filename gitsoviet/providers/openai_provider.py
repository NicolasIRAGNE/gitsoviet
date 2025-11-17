from __future__ import annotations

import base64
from pathlib import Path
from typing import Optional

import requests

from .base import ImageProvider


class OpenAIProvider(ImageProvider):
    """OpenAI image generation API (DALL-E/GPT-Image)."""

    def __init__(self, *, model: str = "gpt-image-1", size: Optional[str] = None) -> None:
        self.model = model
        self.size = size or "1024x1536"

    def generate(self, prompt: str, api_key: str, *, output_path: Path, language: str) -> Path:
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "prompt": prompt,
            "size": self.size,
            "n": 1,
            "response_format": "b64_json",
        }
        response = requests.post("https://api.openai.com/v1/images/generations", json=payload, headers=headers, timeout=60)
        if response.status_code >= 400:
            raise RuntimeError(f"OpenAI image generation failed: {response.status_code} {response.text}")
        body = response.json()
        try:
            raw = body["data"][0]["b64_json"]
        except (KeyError, IndexError) as exc:  # pragma: no cover - defensive
            raise RuntimeError(f"Unexpected OpenAI response: {body}") from exc
        image_bytes = base64.b64decode(raw)
        output_path.write_bytes(image_bytes)
        return output_path
