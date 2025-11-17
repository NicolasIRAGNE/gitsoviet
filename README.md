# gitsoviet

Generate Soviet-era (or intentionally off-brand) propaganda posters for your pull requests. The tool stitches together format and style prompts with PR context, builds an image prompt with Jinja, and renders artwork via pluggable image providers (currently OpenAI image generation).

## How it works
- Base prompt fragments live in `src/gitsoviet/formats/` and `src/gitsoviet/styles/`.
- `gitsoviet` combines the fragments with the PR title, body, changed files, diff, and any extra guidance to create a single prompt.
- Providers live in `gitsoviet.providers`; OpenAI is the default and more can be added by extending the registry.
- The Docker-based GitHub Action and the CLI share the same code path so behavior stays consistent.

## CLI usage
After installing the package (or running inside the container), run:

```bash
python -m gitsoviet.cli \
  --pr-title "Add login flow" \
  --pr-body "Implements OAuth flow" \
  --changed-files "auth.py\nlogin.py" \
  --diff "$(git diff --unified=5 HEAD~1 HEAD)" \
  --guidance "Highlight teamwork" \
  --language "English" \
  --api-key "$OPENAI_API_KEY"
```

CLI flags can also read from a GitHub event payload via `--event-path` or from files using `--pr-body-file` / `--diff-file`. The command prints JSON containing the rendered prompt and the resulting image URL.

## GitHub Action
Use the Docker action directly with `uses: your-org/gitsoviet@main` after publishing, or locally from the repo with `uses: ./.`:

```yaml
- name: Generate propaganda poster
  uses: your-org/gitsoviet@main
  with:
    pr_title: ${{ github.event.pull_request.title }}
    pr_body: ${{ github.event.pull_request.body }}
    changed_files: ${{ steps.diff.outputs.files }}
    diff: ${{ steps.diff.outputs.diff }}
    guidance: "Hail the maintainers"
    api_key: ${{ secrets.OPENAI_API_KEY }}
```

Inputs
- `format`: Poster (default) or Mural
- `style`: Soviet (default), DPRK, Cuban, Capitalist, or Royalist
- `language`: Language for slogans (default: English)
- `guidance`: Additional creative direction
- `provider`: Image generation provider (default: openai)
- `api_key`: Provider API key
- `pr_title`, `pr_body`, `diff`, `changed_files`: PR context (strings, changed files newline-delimited)

The action automatically reads the GitHub event payload for context, and it accepts explicit values for CI steps that collect diffs.

## Workflows
- **CI** (`.github/workflows/ci.yml`): builds the container image on every pull request.
- **Release** (`.github/workflows/release.yml`): pushes the image to GHCR on merges to `main` or tags starting with `v`, `release-`, or `latest`.
- **Ready PR Posters** (`.github/workflows/pr-ready.yml`): when a pull request is marked ready for review, it collects the diff, runs the action with the repo’s secrets, and generates a poster.

## Container
A lightweight Docker image is defined in `Dockerfile`. It packages the CLI and templates, so the same behavior is available locally and inside GitHub Actions.
