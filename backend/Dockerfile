FROM python:3.12-bookworm

ENV PYTHONUNBUFFERED=1

WORKDIR /app/

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Compile bytecode
ENV UV_COMPILE_BYTECODE=1

# uv Cache
ENV UV_LINK_MODE=copy

# Copy dependency files first (for better caching)
COPY ./pyproject.toml /app/

# Install dependencies
# RUN uv sync --frozen --no-install-project

ENV PYTHONPATH=/app

COPY . /app/

# Sync the project
RUN uv sync

CMD ["fastapi", "run", "--workers", "4", "main.py"]