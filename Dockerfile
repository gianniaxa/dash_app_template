FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

# Copy dependency definition and install dependencies
COPY src/pyproject.toml .
RUN uv sync --no-dev

# Copy app source
COPY src/ .

EXPOSE 8050

CMD ["uv", "run", "gunicorn", "--workers", "2", "--bind", "0.0.0.0:8050", "app:server"]
