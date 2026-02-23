#!/bin/bash
set -e

# Models to download
# Format: MODEL_NAME|GGUF_FILE|DOWNLOAD_URL
MODELS=(
    "lfm-thinking|LFM2.5-1.2B-Thinking-Q4_K_M.gguf|https://huggingface.co/LiquidAI/LFM2.5-1.2B-Thinking-GGUF/resolve/main/LFM2.5-1.2B-Thinking-Q4_K_M.gguf?download=true"
)

# Install curl if missing (alpine)
if ! command -v curl &> /dev/null; then
    apk add --no-cache curl
fi

for entry in "${MODELS[@]}"; do
    IFS="|" read -r MODEL_NAME GGUF_FILE DOWNLOAD_URL <<< "$entry"
    
    echo "🔍 Checking for model file: $GGUF_FILE"
    if [ -f "/models/$GGUF_FILE" ] && [ $(stat -c%s "/models/$GGUF_FILE") -gt 1048576 ]; then
        echo "✅ $GGUF_FILE found and appears valid."
    else
        echo "⬇️  $GGUF_FILE not found or invalid. Downloading..."
        curl -L -o "/models/$GGUF_FILE" "$DOWNLOAD_URL"
        echo "✅ Download complete."
    fi
done

echo "🎉 Model Setup Complete."
