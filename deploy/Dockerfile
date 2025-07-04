FROM python:3.13.5-slim-bookworm AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir pipenv==2025.0.3


COPY Pipfile Pipfile.lock ./

ENV PIPENV_VENV_IN_PROJECT=1
RUN pipenv install --deploy --ignore-pipfile


FROM ollama/ollama:latest AS ollama


FROM python:3.13.5-slim-bookworm AS runtime

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libstdc++6 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ollama /bin/ollama /usr/local/bin/ollama
RUN chmod +x /usr/local/bin/ollama

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PYTHONIOENCODING=utf-8 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

COPY --from=builder /app/.venv /app/.venv
# Add virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH"

COPY src/ ./src/
COPY deploy/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh


# Pre-download models during build (increases image size but faster startup)
RUN /usr/local/bin/ollama serve & \
    sleep 15 && \
    /usr/local/bin/ollama pull neural-chat

EXPOSE 8000

ENTRYPOINT [ "/entrypoint.sh" ]


