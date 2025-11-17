FROM python:3.12-slim
WORKDIR /app

# Install dependencies directly
RUN pip install --no-cache-dir Jinja2>=3.1 requests>=2.31 typer>=0.9

# Copy application files
COPY entrypoint.sh ./
COPY gitsoviet ./gitsoviet

# Ensure entrypoint is executable
RUN chmod +x ./entrypoint.sh

ENV PYTHONPATH=/app

ENTRYPOINT ["./entrypoint.sh"]
