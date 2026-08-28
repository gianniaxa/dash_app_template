FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

# The bind-mounted source lives on a different filesystem than the uv cache,
# so hardlinking is unavailable; copy instead of warning on every run.
ENV UV_LINK_MODE=copy

# Copy dependency definition and install dependencies
COPY src/pyproject.toml .
RUN uv sync --no-dev

# Copy app source
COPY src/ .

EXPOSE 8050

CMD ["uv", "run", "gunicorn", "--workers", "2", "--bind", "0.0.0.0:8050", "app:server"]
