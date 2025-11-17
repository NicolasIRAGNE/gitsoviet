from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .prompt_builder import PromptBuilder
from .providers import ProviderRegistry, default_registry


@dataclass
class GenerationRequest:
    pr_title: str
    pr_body: str
    changed_files: Iterable[str]
    diff: str
    guidance: str
    language: str
    format_name: str = "poster"
    style_name: str = "soviet"
    provider: str = "openai"
    api_key: str = ""


@dataclass
class GenerationResult:
    prompt: str
    image_url: str


class PropagandaGenerator:
    def __init__(self, *, prompt_builder: PromptBuilder | None = None, providers: ProviderRegistry | None = None) -> None:
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.providers = providers or default_registry()

    def generate(self, request: GenerationRequest) -> GenerationResult:
        prompt = self.prompt_builder.build(
            format_name=request.format_name,
            style_name=request.style_name,
            title=request.pr_title,
            body=request.pr_body,
            changed_files=request.changed_files,
            diff=request.diff,
            guidance=request.guidance,
            language=request.language,
        )
        provider = self.providers.get(request.provider)
        image_url = provider.generate_image(prompt, api_key=request.api_key)
        return GenerationResult(prompt=prompt, image_url=image_url)
