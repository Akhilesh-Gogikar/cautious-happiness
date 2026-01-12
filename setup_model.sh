#!/bin/bash

MODEL_NAME="openforecaster"
MODEL_DIR="./models"
GGUF_FILE="${MODEL_DIR}/openforecaster.gguf"
DOWNLOAD_URL="https://huggingface.co/mradermacher/OpenForecaster-8B-GGUF/resolve/main/OpenForecaster-8B.Q4_K_M.gguf?download=true"

# Create models directory
mkdir -p "$MODEL_DIR"

# Check if GGUF exists
if [ ! -f "$GGUF_FILE" ]; then
    echo "⬇️  GGUF model not found in ${MODEL_DIR}. Downloading..."
    echo "   URL: $DOWNLOAD_URL"
    curl -L -o "$GGUF_FILE" "$DOWNLOAD_URL"
    
    if [ $? -eq 0 ]; then
        echo "✅ Model downloaded successfully to $GGUF_FILE"
    else
        echo "❌ Download failed."
        exit 1
    fi
else
    echo "✅ GGUF model found at $GGUF_FILE"
fi

echo "Model setup complete! Ready for Docker."
