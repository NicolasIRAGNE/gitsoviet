__all__ = ["create_poster"]

from .generator import PosterGenerator, PosterRequest
from .providers.openai_provider import OpenAIProvider
from .prompt_builder import PromptBuilder

def create_poster(*, provider: OpenAIProvider, request: PosterRequest, templates_path: str | None = None, output_path: str = "poster.png") -> str:
    """Helper used by both CLI and GitHub Action to render and persist a poster image."""
    builder = PromptBuilder(base_path=templates_path)
    generator = PosterGenerator(provider=provider, prompt_builder=builder)
    return str(generator.generate(request=request, output_path=output_path))

