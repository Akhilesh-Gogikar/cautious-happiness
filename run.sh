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
        echo "📝 Please edit .env with your API Keys!"
    else 
        echo "⚠️ No .env or .env.example found. Creating default..."
        echo "GEMINI_API_KEY=" > .env
    fi
fi

# Sign-in tokens need a private signing key. A new .env, or one made from an
# older .env.example, has none or a public placeholder: generate one once.
if ! grep -qE '^SECRET_KEY=[[:space:]]*[^[:space:]]' .env || grep -qE '^SECRET_KEY=(generate_a_secure_random_secret_key|dev_secret_key_change_in_prod_73847384)[[:space:]]*$' .env; then
    SECRET_KEY=$(head -c 32 /dev/urandom | od -An -tx1 | tr -d ' \n')
    if grep -q '^SECRET_KEY=' .env; then
        sed -i.bak "s/^SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env && rm -f .env.bak
    else
        [ -n "$(tail -c1 .env)" ] && echo >> .env
        echo "SECRET_KEY=$SECRET_KEY" >> .env
    fi
    echo "🔑 Generated a private SECRET_KEY in .env."
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
echo "🔐 Sign in with one of the development accounts (README → Signing in)."

echo "ℹ️  Note: The first run may take a few minutes to download the AI model (~730 MB)."
echo "   Check logs with: $DOCKER_COMPOSE logs -f setup_model"

# Follow logs
$DOCKER_COMPOSE logs -f
