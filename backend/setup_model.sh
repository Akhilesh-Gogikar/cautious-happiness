#!/bin/bash
set -e

# Models to download
# Format: MODEL_NAME|GGUF_FILE|DOWNLOAD_URL|REGISTER_IN_OLLAMA
MODELS=(
    "openforecaster|OpenForecaster-8B.Q4_K_M.gguf|https://huggingface.co/mradermacher/OpenForecaster-8B-GGUF/resolve/main/OpenForecaster-8B.Q4_K_M.gguf?download=true|true"
    "lfm-thinking|LFM2.5-1.2B-Thinking-Q4_K_M.gguf|https://huggingface.co/LiquidAI/LFM2.5-1.2B-Thinking-GGUF/resolve/main/LFM2.5-1.2B-Thinking-Q4_K_M.gguf?download=true|false"
)

# Install curl if missing (alpine)
if ! command -v curl &> /dev/null; then
    apk add --no-cache curl
fi

for entry in "${MODELS[@]}"; do
    IFS="|" read -r MODEL_NAME GGUF_FILE DOWNLOAD_URL REGISTER_OLLAMA <<< "$entry"
    
    echo "🔍 Checking for model file: $GGUF_FILE"
    if [ -f "/models/$GGUF_FILE" ] && [ $(stat -c%s "/models/$GGUF_FILE") -gt 1048576 ]; then
        echo "✅ $GGUF_FILE found and appears valid."
    else
        echo "⬇️  $GGUF_FILE not found or invalid. Downloading..."
        curl -L -o "/models/$GGUF_FILE" "$DOWNLOAD_URL"
        echo "✅ Download complete."
    fi

    if [ "$REGISTER_OLLAMA" = "true" ]; then
        OLLAMA_HOST="${OLLAMA_HOST:-http://ollama:11434}"
        echo "⏳ Waiting for Ollama service at $OLLAMA_HOST..."
        until curl -s "$OLLAMA_HOST/api/tags" > /dev/null; do
            sleep 2
        done

        if curl -s "$OLLAMA_HOST/api/tags" | grep -q "$MODEL_NAME"; then
            echo "✅ Model '$MODEL_NAME' already exists in Ollama."
        else
            echo "⚙️  Creating model '$MODEL_NAME' in Ollama..."
            PAYLOAD=$(printf '{"name": "%s", "modelfile": "FROM /models/%s"}' "$MODEL_NAME" "$GGUF_FILE")
            curl -s -X POST "$OLLAMA_HOST/api/create" -H "Content-Type: application/json" -d "$PAYLOAD" > /dev/null
            echo "✅ Model creation trigger sent."
        fi
    fi
done

echo "🎉 Model Setup Complete."
