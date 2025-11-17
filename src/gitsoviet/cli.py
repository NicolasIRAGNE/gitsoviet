from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, List, Sequence

from .generator import GenerationRequest, PropagandaGenerator
from .github import load_pr_from_event


def parse_changed_files(raw: str) -> List[str]:
    return [line for line in raw.replace("\r", "\n").split("\n") if line.strip()]


def read_optional(path: str | None) -> str:
    if not path:
        return ""
    return Path(path).read_text(encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate propaganda posters for GitHub pull requests")
    parser.add_argument("--pr-title", help="Pull request title", default="")
    parser.add_argument("--pr-body", help="Pull request description", default="")
    parser.add_argument("--pr-body-file", help="Path to a file containing the PR body", default=None)
    parser.add_argument("--diff", help="Pull request diff text", default="")
    parser.add_argument("--diff-file", help="Path to a file containing the diff", default=None)
    parser.add_argument("--changed-files", help="Newline-delimited list of changed files", default="")
    parser.add_argument("--format", dest="format_name", help="Poster format (poster or mural)", default="poster")
    parser.add_argument("--style", dest="style_name", help="Art style", default="soviet")
    parser.add_argument("--language", help="Language for slogans", default="English")
    parser.add_argument("--guidance", help="Additional creative guidance", default="")
    parser.add_argument("--provider", help="Image provider", default="openai")
    parser.add_argument("--api-key", help="Provider API key", default="")
    parser.add_argument("--event-path", help="Path to a GitHub event payload", default=None)
    parser.add_argument("--output", help="Path to write JSON result", default=None)
    return parser


def resolve_pr_fields(args: argparse.Namespace) -> tuple[str, str, List[str], str]:
    if args.event_path:
        event_data = json.loads(Path(args.event_path).read_text(encoding="utf-8"))
        pr_data = load_pr_from_event(event_data)
        if pr_data:
            return pr_data.title, pr_data.body, pr_data.changed_files, pr_data.diff
    body = args.pr_body or read_optional(args.pr_body_file)
    diff = args.diff or read_optional(args.diff_file)
    changed_files = parse_changed_files(args.changed_files)
    return args.pr_title, body, changed_files, diff


def create_request(args: argparse.Namespace) -> GenerationRequest:
    title, body, changed_files, diff = resolve_pr_fields(args)
    return GenerationRequest(
        pr_title=title,
        pr_body=body,
        changed_files=changed_files,
        diff=diff,
        guidance=args.guidance,
        language=args.language,
        format_name=args.format_name,
        style_name=args.style_name,
        provider=args.provider,
        api_key=args.api_key,
    )


def run(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    request = create_request(args)
    generator = PropagandaGenerator()
    result = generator.generate(request)

    output = {"prompt": result.prompt, "image_url": result.image_url}
    if args.output:
        Path(args.output).write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
