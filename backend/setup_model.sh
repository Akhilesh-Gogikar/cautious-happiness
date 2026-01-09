#!/bin/bash
set -e

MODEL_NAME="openforecaster"
GGUF_FILE="OpenForecaster-8B.Q4_K_M.gguf"
# Direct download link for the specific model version (example link, need to verify exact URL or use huggingface-cli if installed)
# Using a reliable mirror or the main HF link.
# Model: https://huggingface.co/mRadam/OpenForecaster-8B-GGUF/resolve/main/OpenForecaster-8B.Q4_K_M.gguf
DOWNLOAD_URL="https://huggingface.co/mRadam/OpenForecaster-8B-GGUF/resolve/main/OpenForecaster-8B.Q4_K_M.gguf"

DATA_DIR="/root/.ollama" 
# In our docker-compose, we might map a volume to /models or similar. 
# We need to agree on where the model file lives relative to the ollama container.

echo "🔍 Checking for model file: $GGUF_FILE"

if [ -f "/models/$GGUF_FILE" ]; then
    echo "✅ Model file found."
else
    echo "⬇️  Model file not found. Downloading from Hugging Face..."
    echo "   URL: $DOWNLOAD_URL"
    # Install curl if missing (alpine)
    if ! command -v curl &> /dev/null; then
        apk add --no-cache curl
    fi
    
    curl -L -o "/models/$GGUF_FILE" "$DOWNLOAD_URL"
    echo "✅ Download complete."
fi

# Now we need to create the model in Ollama
# This script is intended to run in a container that has access to the ollama service OR is the ollama init.
# If this is a separate 'init' container, it needs to talk to 'ollama' host.

OLLAMA_HOST="${OLLAMA_HOST:-http://ollama:11434}"

echo "⏳ Waiting for Ollama service at $OLLAMA_HOST..."
until curl -s "$OLLAMA_HOST/api/tags" > /dev/null; do
    sleep 2
    echo "   ...waiting for ollama"
done

echo "🔍 Checking if model '$MODEL_NAME' exists..."
if curl -s "$OLLAMA_HOST/api/tags" | grep -q "$MODEL_NAME"; then
    echo "✅ Model '$MODEL_NAME' already exists in Ollama."
else
    echo "⚙️  Creating model '$MODEL_NAME'..."
    
    # We need to send a create request. 
    # Since the GGUF is on a shared volume, we need to know the path *inside the ollama container*.
    # Let's assume we map ./backend/models (host) -> /models (init container) AND -> /models (ollama container).
    
    # Create a minimal Modelfile payload
    # The path must be valid INSIDE the ollama container.
    PAYLOAD="{\"name\": \"$MODEL_NAME\", \"modelfile\": \"FROM /models/$GGUF_FILE\"}"
    
    RESPONSE=$(curl -s -X POST "$OLLAMA_HOST/api/create" -d "$PAYLOAD")
    echo "   Response: $RESPONSE"
    echo "✅ Model creation trigger sent."
fi

echo "🎉 Model Setup Complete."
