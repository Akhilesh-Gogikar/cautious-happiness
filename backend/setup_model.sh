#!/bin/bash
set -e

# Models to download
# Format: MODEL_NAME|GGUF_FILE|DOWNLOAD_URL
MODELS=(
    "lfm-thinking|LFM2.5-1.2B-Thinking-Q4_K_M.gguf|https://huggingface.co/LiquidAI/LFM2.5-1.2B-Thinking-GGUF/resolve/main/LFM2.5-1.2B-Thinking-Q4_K_M.gguf?download=true"
)
MODELS_DIR="${MODELS_DIR:-/models}"

# Install curl if missing (alpine)
if ! command -v curl &> /dev/null; then
    apk add --no-cache curl
fi

# Size the server reports for the file (the last Content-Length after
# redirects), or nothing when it can't be reached.
remote_size() {
    curl -fsIL --max-time 30 "$1" 2>/dev/null | tr -d '\r' \
        | awk 'tolower($1) == "content-length:" { size = $2 } END { print size }'
}

for entry in "${MODELS[@]}"; do
    IFS="|" read -r MODEL_NAME GGUF_FILE DOWNLOAD_URL <<< "$entry"
    TARGET="$MODELS_DIR/$GGUF_FILE"
    PART="$TARGET.part"

    echo "🔍 Checking for model file: $GGUF_FILE"
    EXPECTED=$(remote_size "$DOWNLOAD_URL")
    if [ -f "$TARGET" ]; then
        SIZE=$(stat -c%s "$TARGET")
        # A file left by an interrupted download (older versions of this script
        # wrote straight to the final name) is shorter than the remote file.
        # Offline, fall back to a plausibility check so restarts still work.
        if { [ -n "$EXPECTED" ] && [ "$SIZE" = "$EXPECTED" ]; } || { [ -z "$EXPECTED" ] && [ "$SIZE" -gt 1048576 ]; }; then
            echo "✅ $GGUF_FILE found and appears valid."
            continue
        fi
        echo "⚠️  $GGUF_FILE is $SIZE bytes, expected ${EXPECTED:-more}; downloading it again."
        rm -f "$TARGET"
    fi

    echo "⬇️  Downloading $GGUF_FILE..."
    # Download to a temporary name and rename when complete, so an interrupted
    # or failed download is never mistaken for the model. -f fails on HTTP
    # errors instead of saving the error page; -C - resumes a .part left by an
    # earlier attempt; --retry-all-errors also retries dropped connections.
    if [ -n "$EXPECTED" ] && [ -f "$PART" ] && [ "$(stat -c%s "$PART")" -ge "$EXPECTED" ]; then
        rm -f "$PART"  # nothing left to resume
    fi
    curl -fL --retry 5 --retry-all-errors -C - -o "$PART" "$DOWNLOAD_URL"
    SIZE=$(stat -c%s "$PART")
    if [ -n "$EXPECTED" ] && [ "$SIZE" != "$EXPECTED" ]; then
        echo "❌ Downloaded $SIZE bytes, expected $EXPECTED. Run setup_model again to resume."
        exit 1
    fi
    mv "$PART" "$TARGET"
    echo "✅ Download complete."
done

echo "🎉 Model Setup Complete."
