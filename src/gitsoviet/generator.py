from __future__ import annotations

from pathlib import Path

from .prompt_builder import PromptBuilder
from .request import PosterRequest
from .providers.base import ImageProvider


class PosterGenerator:
    """Coordinates prompt rendering and provider invocation."""

    def __init__(self, *, provider: ImageProvider, prompt_builder: PromptBuilder) -> None:
        self.provider = provider
        self.prompt_builder = prompt_builder

    def generate(self, *, request: PosterRequest, output_path: str | Path) -> Path:
        prompt = self.prompt_builder.build(request=request)
        image_bytes = self.provider.generate_image(prompt=prompt, request=request)
        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(image_bytes)
        return target

