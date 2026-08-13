FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install uv for fast package management
RUN pip install --no-cache-dir uv

# Copy dependency files first to cache heavy packages
COPY pyproject.toml uv.lock ./

# Install dependencies using Docker cache mount for lightning-fast builds
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Copy the rest of your application code
COPY . .

EXPOSE 8001

CMD ["uv", "run", "python", "server.py"]