#!/usr/bin/env sh
set -euo pipefail

OUTPUT_PATH="${GITSOVIET_OUTPUT:-poster.png}"
EXPECT_VALUE=""
for arg in "$@"; do
    if [ "$EXPECT_VALUE" = "output" ]; then
        OUTPUT_PATH="$arg"
        EXPECT_VALUE=""
        continue
    fi
    case "$arg" in
        --output-path)
            EXPECT_VALUE="output"
            ;;
        --output-path=*)
            OUTPUT_PATH="${arg#*=}"
            ;;
    esac
done

gitsoviet "$@"

if [ -n "${GITHUB_OUTPUT:-}" ]; then
    resolved_path="$(python -c 'import os,sys;print(os.path.abspath(sys.argv[1]))' "$OUTPUT_PATH")"
    printf 'image-path=%s\n' "$resolved_path" >> "$GITHUB_OUTPUT"
fi
