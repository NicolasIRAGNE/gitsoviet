from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer

from .generator import PosterGenerator
from .prompt_builder import PromptBuilder
from .providers.openai_provider import OpenAIProvider
from .request import PosterRequest

app = typer.Typer(add_completion=False, help="Generate propaganda art from code changes.")


def _read_text(value: str, file_path: Optional[Path]) -> str:
    if file_path:
        return file_path.read_text(encoding="utf-8")
    return value


def _resolve_stream(default: str) -> str:
    if default:
        return default
    if not sys.stdin.isatty():
        return sys.stdin.read()
    return ""


@app.command()
def generate(
    repo_name: str = typer.Option(..., help="Repository name (e.g. org/repo)."),
    pr_title: str = typer.Option(..., help="Pull request title."),
    pr_title_file: Optional[Path] = typer.Option(None, help="Path to a file containing the PR title."),
    pr_description: str = typer.Option("", help="Pull request description."),
    pr_description_file: Optional[Path] = typer.Option(None, help="Path to a file containing the PR description."),
    pr_author: str = typer.Option(..., help="Pull request author."),
    diff: str = typer.Option("", help="Unified diff to feed into the prompt."),
    diff_file: Optional[Path] = typer.Option(None, help="Path to a file containing the diff."),
    additional_prompt: str = typer.Option("", help="Extra creative guidance appended to the prompt."),
    additional_prompt_file: Optional[Path] = typer.Option(None, help="File containing extra creative guidance."),
    format: str = typer.Option("poster", help="poster or mural"),
    style: str = typer.Option("soviet", help="soviet, dprk, cuban, capitalist, royalist"),
    language: str = typer.Option("English", help="Language for textual elements on the poster."),
    provider: str = typer.Option("openai", help="Image generation backend."),
    api_key: Optional[str] = typer.Option(None, envvar="OPENAI_API_KEY", help="API key for the provider."),
    model: str = typer.Option("gpt-image-1", help="Model to use for image generation."),
    size: Optional[str] = typer.Option(None, help="Image size override, e.g. 1024x1024."),
    output: Path = typer.Option(Path("poster.png"), help="Where to save the generated image."),
    templates_path: Optional[Path] = typer.Option(None, help="Override the default template directory."),
) -> None:
    provider_key = provider.strip().lower()
    if provider_key != "openai":
        raise typer.BadParameter("Only the OpenAI provider is implemented right now.")
    if not api_key:
        raise typer.BadParameter("Supply an API key via --api-key or OPENAI_API_KEY env var.")

    pr_title_text = _read_text(pr_title, pr_title_file)
    pr_description_text = _read_text(pr_description, pr_description_file)
    diff_text = _resolve_stream(_read_text(diff, diff_file))
    extra_text = _read_text(additional_prompt, additional_prompt_file)

    request = PosterRequest(
        repo_name=repo_name,
        pr_title=pr_title_text,
        pr_description=pr_description_text,
        pr_author=pr_author,
        diff=diff_text,
        format=format,
        style=style,
        language=language,
        additional_prompt=extra_text,
    )

    prompt_builder = PromptBuilder(base_path=templates_path)
    generator = PosterGenerator(
        provider=OpenAIProvider(api_key=api_key, model=model, size=size or None),
        prompt_builder=prompt_builder,
    )
    image_path = generator.generate(request=request, output_path=output)
    typer.echo(f"Poster saved to {image_path}")


if __name__ == "__main__":  # pragma: no cover
    app()


