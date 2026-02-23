#!/bin/bash

MODEL_NAME="openforecaster"
GGUF_FILE="OpenForecaster-8B.Q4_K_M.gguf"
DOWNLOAD_URL="https://huggingface.co/mradermacher/OpenForecaster-8B-GGUF/resolve/main/OpenForecaster-8B.Q4_K_M.gguf?download=true"

# 1. Download model if missing
if [ ! -f "/models/$GGUF_FILE" ]; then
    echo "GGUF model not found in /models. Downloading to shared volume..."
    curl -L -o "/models/$GGUF_FILE" "$DOWNLOAD_URL"
else
    echo "GGUF model found at /models/$GGUF_FILE"
fi

# 2. Wait for Ollama to be ready
echo "Waiting for Ollama at $OLLAMA_HOST..."
MAX_RETRIES=30
COUNT=0
until curl -s "$OLLAMA_HOST/api/tags" > /dev/null; do
    COUNT=$((COUNT+1))
    if [ $COUNT -ge $MAX_RETRIES ]; then
        echo "Ollama timed out."
        exit 1
    fi
    echo "Retrying Ollama ($COUNT/$MAX_RETRIES)..."
    sleep 2
done

# 3. Create model only if not exists
if ollama list | grep -q "$MODEL_NAME"; then
    echo "Model '$MODEL_NAME' already exists in Ollama. Skipping creation."
else
    echo "Creating Ollama model '$MODEL_NAME'..."
    ollama create "$MODEL_NAME" -f Modelfile
fi

echo "Setup complete. Model '$MODEL_NAME' is ready."
