# GitSoviet

`gitsoviet` turns GitHub pull requests into tongue-in-cheek propaganda posters.  
It inspects a PR (title, description, diff), stitches the context together with
format/style base prompts via Jinja, and sends the resulting prompt to an image
generation provider (OpenAI for now). The same code path powers both the CLI
and the reusable GitHub Action so you can call it locally or from workflows.

## Quick start (CLI)

```bash
pip install .
export GITHUB_TOKEN=<token with repo:read>
export OPENAI_API_KEY=<image api key>
gitsoviet generate --repo your-org/your-repo --pr-number 123 --output-path poster.png
```

Useful flags:

- `--format-name poster|mural`
- `--style-name soviet|dprk|cuban|capitalist|royalist`
- `--language <text language>`
- `--extra-guidance "Add slogans about CI"`
- `--provider openai` (extensible registry for future providers)

The command auto-detects repo/PR when it runs inside GitHub Actions by reading
`GITHUB_EVENT_PATH`.

## Base prompt fragments

Each format and style has its own text fragment under `gitsoviet/data`. Adding
new variants is as simple as dropping a `*.txt` file in `formats/` or `styles/`.
The prompt is rendered via `gitsoviet/templates/prompt.j2`.

## GitHub Action

Published as a container action so it can be consumed with plain `uses` syntax.

```yaml
- name: Sovietize this PR
  uses: your-org/gitsoviet@main
  with:
    api-key: ${{ secrets.OPENAI_API_KEY }}
    additional-guidance: "Glorify the reviewer collective"
    language: "English"
```

Inputs:

- `api-key` (required)
- `github-token` (defaults to `${{ github.token }}`)
- `additional-guidance`, `language`, `format`, `style`, `provider`, `output-file`

Output `image-path` contains the absolute path to the rendered asset (useful for
artifact upload steps).

## Workflows included

1. **build** (`.github/workflows/pr-build.yml`) – builds the container image on every PR.
2. **publish** (`.github/workflows/publish.yml`) – pushes the image to GHCR on merges to `main` and tags (`v*`).
3. **revolutionary** (`.github/workflows/revolutionary.yml`) – whenever a PR is ready for review and carries the `revolutionary` label, it runs the action automatically (requires `OPENAI_API_KEY` secret) and uploads the poster as an artifact.

## Container image

The repo ships with a `Dockerfile` and `action.yml`. The publish workflow tags
images as:

- `ghcr.io/<owner>/gitsoviet:<sha>`
- `ghcr.io/<owner>/gitsoviet:latest` (main branch)
- `ghcr.io/<owner>/gitsoviet:<tag>` (tags starting with `v`)

## Extending providers

Providers live under `gitsoviet/providers`. Register a new backend with
`registry.register("name", lambda **kwargs: Provider(**kwargs))` and the CLI +
action automatically accept `--provider name`.
