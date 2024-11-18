FROM python:3.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_NO_CACHE=1

COPY pyproject.toml pyproject.toml
COPY uv.lock uv.lock
 
RUN uv sync
 
COPY src src