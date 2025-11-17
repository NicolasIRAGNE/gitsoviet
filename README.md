# gitsoviet

Reusable GitHub Actions workflow that reviews pull requests and responds with a Soviet-style propaganda poster generated via the ChatGPT Image API (or compatible providers).

## Usage
Call the workflow from another workflow in the same or different repository. Provide the pull request number and an `openai_api_key` secret with access to your image generation endpoint.

```yaml
name: PR Propaganda Review

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  propaganda:
    uses: <owner>/<repo>/.github/workflows/propaganda-review.yml@main
    with:
      pull_number: ${{ github.event.pull_request.number }}
      image_prompt: "Add a rocket launch and code motifs."
    secrets:
      openai_api_key: ${{ secrets.OPENAI_API_KEY }}
```

## Inputs
- `pull_number` (**required**): Target pull request number.
- `image_prompt` (optional): Extra art direction appended to the generated prompt.
- `image_api` (optional): Label for the provider (defaults to `openai`).
- `openai_model` (optional): Model name for the image endpoint (defaults to `gpt-image-1`).
- `openai_base_url` (optional): Base URL for an OpenAI-compatible image generation endpoint (defaults to `https://api.openai.com/v1`).

## Secrets
- `openai_api_key` (**required**): API key for the ChatGPT Image API or compatible service.

## Permissions
The workflow requests `pull-requests: write` to post the image comment and `contents: read` for repository access.
