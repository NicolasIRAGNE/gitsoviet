FROM python:3.12-slim AS base
WORKDIR /app

# Install runtime dependencies
RUN python -m pip install --upgrade pip

COPY pyproject.toml README.md entrypoint.sh ./
COPY gitsoviet ./gitsoviet

RUN pip install --no-cache-dir .

ENTRYPOINT ["./entrypoint.sh"]
