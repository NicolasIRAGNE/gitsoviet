from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Protocol

from openai import OpenAI


class ImageProvider(Protocol):
    def generate_image(self, prompt: str, *, api_key: str) -> str:
        """Generate an image and return the URL to the generated asset."""


@dataclass
class ProviderRegistry:
    providers: Dict[str, ImageProvider]

    def get(self, name: str) -> ImageProvider:
        normalized = name.lower()
        if normalized not in self.providers:
            available = ", ".join(sorted(self.providers)) or "none"
            raise ValueError(f"Unknown provider '{name}'. Available: {available}")
        return self.providers[normalized]


class OpenAIProvider:
    def generate_image(self, prompt: str, *, api_key: str) -> str:
        client = OpenAI(api_key=api_key)
        response = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024",
            response_format="url",
        )
        return response.data[0].url


def default_registry() -> ProviderRegistry:
    return ProviderRegistry(providers={"openai": OpenAIProvider()})
