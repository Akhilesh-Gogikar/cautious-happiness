#!/bin/bash

MODEL_NAME="openforecaster"
GGUF_FILE="OpenForecaster-8B.Q4_K_M.gguf"
DOWNLOAD_URL="https://huggingface.co/mradermacher/OpenForecaster-8B-GGUF/resolve/main/OpenForecaster-8B.Q4_K_M.gguf?download=true"

# Check if GGUF exists
if [ ! -f "$GGUF_FILE" ]; then
    echo "GGUF model not found locally. Downloading..."
    curl -L -o "$GGUF_FILE" "$DOWNLOAD_URL"
else
    echo "GGUF model found at $GGUF_FILE"
fi

# Check if Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    echo "Ollama is not running. Please start Ollama first."
    exit 1
fi

echo "Creating Ollama model '$MODEL_NAME'..."
ollama create "$MODEL_NAME" -f Modelfile

echo "Model '$MODEL_NAME' setup complete!"
echo "You can now run: ollama run $MODEL_NAME"
