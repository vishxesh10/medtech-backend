FROM python:3.12-slim
WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv \
    && uv sync --frozen --no-dev --no-install-project

COPY . .
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000

CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}"]
