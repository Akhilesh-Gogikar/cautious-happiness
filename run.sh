#!/bin/bash

# Polymarket Dashboard Launcher

echo "🚀 Initializing Hedge Fund Dashboard Protocol..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "⚠️ docker-compose not found, trying 'docker compose'..."
    if ! docker compose version &> /dev/null; then
        echo "❌ Docker Compose not found."
        exit 1
    fi
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

echo "✅ Docker detected."

# Check for .env
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo "⚠️ No .env file found. Creating from .env.example..."
        cp .env.example .env
        # A private key for signing sign-in tokens (never the placeholder).
        SECRET_KEY=$(head -c 32 /dev/urandom | od -An -tx1 | tr -d ' \n')
        sed -i.bak "s/^SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env && rm -f .env.bak
        echo "📝 Please edit .env with your API Keys!"
    else 
        echo "⚠️ No .env or .env.example found. Creating default..."
        echo "GEMINI_API_KEY=" > .env
    fi
fi

# Build and Run
echo "🏗️  Building Container Stack..."
# We use --remove-orphans to clean up old containers
$DOCKER_COMPOSE up --build -d --remove-orphans

echo "⏳ Waiting for services to stabilize..."
sleep 5

echo "✅ System Online."
echo "📊 Dashboard: http://localhost:3000"
echo "🔌 API:       http://localhost:8000"

echo "ℹ️  Note: The first run may take a few minutes to download the AI model (~730 MB)."
echo "   Check logs with: $DOCKER_COMPOSE logs -f setup_model"

# Follow logs
$DOCKER_COMPOSE logs -f
