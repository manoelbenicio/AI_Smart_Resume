FROM python:3.12-slim AS builder

WORKDIR /app

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

COPY pyproject.toml README.md ./
COPY src ./src

RUN python -m pip install --upgrade pip && \
    python -m pip install --prefix=/install ".[dev]"


FROM python:3.12-slim AS runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    OUTPUT_DIR=/app/outputs

COPY --from=builder /install /usr/local
COPY src ./src
COPY tests ./tests
COPY pyproject.toml README.md ./

RUN mkdir -p /app/outputs

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "smart_resume.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
