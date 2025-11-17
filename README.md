# gitsoviet

Generate over-the-top propaganda artwork that celebrates your pull requests. The project ships a Python CLI, a Docker image, and a reusable GitHub Action so you can create Soviet/DPRK/Cuban/etc. styled posters from PR metadata and diffs.

## Features
- Jinja-driven prompt builder that mixes base, format, and style templates with any PR title, description, author, repo, and diff.
- Provider abstraction with an OpenAI backend today and room for other image APIs later.
- Format selection automatically drives canvas orientation: posters are portrait, murals are landscape.
- CLI and Docker entrypoint share the exact same code path.
- First-class GitHub Action (`action.yml`) so other repos can run `uses: owner/gitsoviet@main` with their own API keys and guidance.
- Automated workflows:
  - `gitsoviet CI` builds/tests and ensures the Dockerfile keeps working on every PR.
  - `Publish Image` pushes the container to `ghcr.io/<org>/<repo>` on `main` merges and tags.
  - `Revolutionary Posters` watches for the `revolutionary` label and generates an artifact by running the latest GHCR image.

## Local development
1. Install Python 3.11+.
2. (Optional) create a virtualenv and install editable dependencies:
   ```powershell
   pip install -e .
   ```
3. Supply an OpenAI key via `.env` or the environment (`OPENAI_API_KEY`).
4. Run the CLI:
   ```powershell
   python -m gitsoviet \
     --repo-name your-org/your-repo \
     --pr-title "Add revolutionary workflow" \
     --pr-author your-handle \
     --diff-file example.diff \
     --language English \
     --style soviet \
     --format poster \
     --output poster.png
   ```

## Docker usage
The Dockerfile installs the package and sets `gitsoviet` as the entrypoint. Build/run manually:
```powershell
# Build
docker build -t ghcr.io/you/gitsoviet:dev .

# Run (mount workspace for reading diffs / writing poster)
docker run --rm \
  -e OPENAI_API_KEY \
  -v ${PWD}:/work \
  -w /work \
  ghcr.io/you/gitsoviet:dev \
  --repo-name your-org/your-repo \
  --pr-title-file pr_title.txt \
  --pr-description-file pr_description.txt \
  --pr-author your-handle \
  --diff-file pr.diff
```

## GitHub Action
Reference the reusable action straight from a workflow:
```yaml
jobs:
  poster:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Capture diff
        id: diff
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          gh pr diff ${{ github.event.pull_request.number }} --repo ${{ github.repository }} > pr.diff
          {
            echo "diff<<'EOF'"
            cat pr.diff
            echo 'EOF'
          } >> "$GITHUB_OUTPUT"
      - name: Generate poster
        uses: owner/gitsoviet@main
        with:
          repo-name: ${{ github.repository }}
          pr-title: ${{ github.event.pull_request.title }}
          pr-description: ${{ github.event.pull_request.body }}
          pr-author: ${{ github.event.pull_request.user.login }}
          diff: ${{ steps.diff.outputs.diff }}
          api-key: ${{ secrets.OPENAI_API_KEY }}
          language: English
          additional-prompt: |
            Glorify the maintainer collective.
```
Inputs exposed via the action: format (`poster` or `mural`), style (`soviet`, `dprk`, `cuban`, `capitalist`, `royalist`), language, provider (openai), additional-prompt, model, size override, output path, and the required API key.

## Built-in workflows
- **`gitsoviet CI`** – installs the package, compiles the source tree, and builds the container on every PR.
- **`Publish Image`** – builds the Docker image and pushes `ghcr.io/<repo>:sha` (plus `:latest` or the tag name) whenever `main` updates or a semver tag is created.
- **`Revolutionary Posters`** – runs on `pull_request_target` whenever the PR carries the `revolutionary` label. It downloads the diff via `gh pr diff`, feeds repository variables for language/format/style/additional prompt, executes the GHCR image, and uploads `revolutionary-poster` as an artifact. Configure the workflow by setting these repo variables (optional):
  - `GITSOVIET_LANGUAGE`
  - `GITSOVIET_FORMAT`
  - `GITSOVIET_STYLE`
  - `GITSOVIET_ADDITIONAL_PROMPT`

All workflows expect an `OPENAI_API_KEY` secret at the repo level.

## Extending providers
`gitsoviet.providers.base.ImageProvider` defines the interface. Implement a new provider and wire it inside `cli.py` to support another model. Prompt templates live under `src/gitsoviet/templates/` and can be extended with new files in `formats/` or `styles/`.


