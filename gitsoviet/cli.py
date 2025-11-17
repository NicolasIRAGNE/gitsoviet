from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import typer

from .github_client import GitHubClient
from .prompt_builder import PromptBuilder, PromptContext, summarize_files
from .providers import OpenAIProvider, ProviderRegistry

app = typer.Typer(help="Generate propaganda posters from GitHub pull requests")

DATA_DIR = Path(__file__).resolve().parent / "data"
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

registry = ProviderRegistry()
registry.register("openai", lambda **kwargs: OpenAIProvider(**kwargs))


def _infer_from_event(event_path: Optional[Path]) -> tuple[Optional[str], Optional[int]]:
    if not event_path or not event_path.exists():
        return None, None
    data = json.loads(event_path.read_text(encoding="utf-8"))
    repo = data.get("repository", {}).get("full_name")
    pr_number = None
    if "pull_request" in data:
        pr_number = data["pull_request"].get("number")
    elif "issue" in data and data["issue"].get("pull_request"):
        pr_number = data["issue"].get("number")
    elif "workflow_run" in data and data["workflow_run"].get("pull_requests"):
        pull_requests = data["workflow_run"].get("pull_requests") or []
        if pull_requests:
            pr_number = pull_requests[0].get("number")
            repo = repo or data["workflow_run"].get("repository", {}).get("full_name")
    return repo, pr_number


def _resolve_repo_and_pr(
    repo: Optional[str], pr_number: Optional[int], event_path: Optional[Path]
) -> tuple[str, int]:
    inferred_repo, inferred_pr = _infer_from_event(event_path)
    repo = repo or inferred_repo or os.environ.get("GITHUB_REPOSITORY")
    pr_number = pr_number or inferred_pr
    if not repo:
        raise typer.BadParameter("Repository must be provided via --repo or GITHUB_REPOSITORY")
    if not pr_number:
        raise typer.BadParameter("Pull request number missing. Provide --pr-number or event context")
    return repo, int(pr_number)


def _determine_size(format_name: str) -> str:
    if format_name.lower() == "mural":
        return "1536x1024"
    return "1024x1536"


@app.command(name="generate")
def generate(
    repo: Optional[str] = typer.Option(None, help="target repository, e.g. org/repo"),
    pr_number: Optional[int] = typer.Option(None, help="pull request number"),
    github_token: Optional[str] = typer.Option(None, envvar="GITHUB_TOKEN", help="GitHub token"),
    api_key: Optional[str] = typer.Option(None, envvar="OPENAI_API_KEY", help="Image provider API key"),
    format_name: str = typer.Option("poster", help="Poster or mural"),
    style_name: str = typer.Option("soviet", help="Visual style variant"),
    language: str = typer.Option("English", help="Language to use for narration"),
    provider: str = typer.Option("openai", help="Image provider identifier"),
    extra_guidance: str = typer.Option("", help="Extra text appended to the prompt"),
    output_path: Path = typer.Option(Path("poster.png"), help="Where to store the generated image"),
    event_path: Optional[Path] = typer.Option(None, help="Path to GitHub event payload"),
) -> None:
    if event_path is None:
        env_event = os.environ.get("GITHUB_EVENT_PATH")
        if env_event:
            event_path = Path(env_event)

    repo, pr_number = _resolve_repo_and_pr(repo, pr_number, event_path)
    if not api_key:
        raise typer.BadParameter("API key must be provided via --api-key or OPENAI_API_KEY")

    builder = PromptBuilder(data_dir=DATA_DIR, templates_dir=TEMPLATES_DIR)
    gh = GitHubClient(token=github_token)

    pr_info = gh.get_pull_request(repo, pr_number)
    pr_files = gh.get_pull_request_files(repo, pr_number)
    diff_summary = summarize_files(pr_files) or "No file changes detected"

    prompt = builder.build(
        PromptContext(
            format_name=format_name,
            style_name=style_name,
            language=language,
            pr_title=pr_info.title,
            pr_body=pr_info.body or "No description",
            diff_summary=diff_summary,
            extra_guidance=extra_guidance or "",
        )
    )

    provider_instance = registry.create(provider, size=_determine_size(format_name))
    result_path = provider_instance.generate(prompt, api_key, output_path=output_path, language=language)
    typer.echo(f"Poster stored at {result_path}")
