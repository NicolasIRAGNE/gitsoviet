#!/usr/bin/env bash
set -euo pipefail

ARGS=(
  "--format" "${INPUT_FORMAT:-poster}"
  "--style" "${INPUT_STYLE:-soviet}"
  "--language" "${INPUT_LANGUAGE:-English}"
  "--guidance" "${INPUT_GUIDANCE:-}"
  "--provider" "${INPUT_PROVIDER:-openai}"
)

if [[ -n "${INPUT_PR_TITLE:-}" ]]; then
  ARGS+=("--pr-title" "${INPUT_PR_TITLE}")
fi
if [[ -n "${INPUT_PR_BODY:-}" ]]; then
  ARGS+=("--pr-body" "${INPUT_PR_BODY}")
fi
if [[ -n "${INPUT_DIFF:-}" ]]; then
  ARGS+=("--diff" "${INPUT_DIFF}")
fi
if [[ -n "${INPUT_CHANGED_FILES:-}" ]]; then
  ARGS+=("--changed-files" "${INPUT_CHANGED_FILES}")
fi

API_KEY="${INPUT_API_KEY:-${OPENAI_API_KEY:-}}"
if [[ -n "${API_KEY}" ]]; then
  ARGS+=("--api-key" "${API_KEY}")
fi

if [[ -n "${GITHUB_EVENT_PATH:-}" && -f "${GITHUB_EVENT_PATH}" ]]; then
  ARGS+=("--event-path" "${GITHUB_EVENT_PATH}")
fi

python -m gitsoviet.cli "${ARGS[@]}"
