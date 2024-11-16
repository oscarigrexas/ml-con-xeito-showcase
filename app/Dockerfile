FROM python:3.11
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml pyproject.toml
COPY uv.lock uv.lock
 
RUN uv sync
 
COPY src src