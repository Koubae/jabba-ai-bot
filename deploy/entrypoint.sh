#!/usr/bin/env bash
set -euo pipefail


# Check if BOT_ML_MODEL is not set to "testings-mock", if so, start Ollama
if [[ "${BOT_ML_MODEL:-}" != "testings-mock" ]]; then
    echo "Loading Ollama ML service"
    # Start Ollama in background
    /usr/local/bin/ollama serve &

    # Wait for Ollama to be ready
    sleep 10

    echo "Ollama ready, starting application..."
else
    echo "BOT_ML_MODEL is set to testings-mock, skipping Ollama startup..."
fi

exec "$@"