from __future__ import annotations

import base64
from dataclasses import dataclass

from openai import OpenAI

from .base import ImageProvider
from ..request import PosterRequest


@dataclass(slots=True)
class OpenAIProvider(ImageProvider):
    api_key: str
    model: str = "gpt-image-1"
    size: str | None = None

    def __post_init__(self) -> None:
        if not self.api_key:
            raise ValueError("An OpenAI API key is required to generate images.")
        self.client = OpenAI(api_key=self.api_key)

    def generate_image(self, *, prompt: str, request: PosterRequest) -> bytes:
        size = self.size or request.image_size
        try:
            response = self.client.images.generate(
                model=self.model,
                prompt=prompt,
                size=size,
            )
        except Exception as exc:  # pragma: no cover - network call
            raise RuntimeError("OpenAI image generation failed") from exc
        image_base64 = response.data[0].b64_json
        return base64.b64decode(image_base64)
