FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .

# /data is where Railway mounts the persistent volume
RUN mkdir -p /data

CMD ["uv", "run", "python", "shortlink_bot.py"]
