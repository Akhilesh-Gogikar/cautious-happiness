version: '3.8'

services:
  # ----------------------------------------------------------------
  # 1. THE BRAIN: Python FastAPI Backend + RAG Engine
  # ----------------------------------------------------------------
  backend:
    build: ./backend
    container_name: poly_brain
    restart: always
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/polymarket_db
      - REDIS_URL=redis://redis:6379/0
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - POLYMARKET_API_URL=https://clob.polymarket.com
      - OLLAMA_HOST=http://ollama:11434
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
      - ollama
    networks:
      - poly_net

  # ----------------------------------------------------------------
  # 2. THE LOCAL LLM: Ollama (Runs OpenForecaster)
  # ----------------------------------------------------------------
  ollama:
    image: ollama/ollama:latest
    container_name: poly_llm
    restart: always
    volumes:
      - ollama_data:/root/.ollama
    ports:
      - "11434:11434"
    networks:
      - poly_net
    # Deploy logic: On first run, we will exec into this to pull the model
    # command: "ollama pull qwen2.5:7b" (We will use Qwen as base for OpenForecaster)

  # ----------------------------------------------------------------
  # 3. THE WORKER: Background Intelligence
  # ----------------------------------------------------------------
  worker:
    build: ./backend
    container_name: poly_worker
    command: celery -A app.worker worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/polymarket_db
      - REDIS_URL=redis://redis:6379/0
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - OLLAMA_HOST=http://ollama:11434
    depends_on:
      - db
      - redis
      - ollama
    networks:
      - poly_net

  # ----------------------------------------------------------------
  # 4. THE FACE: Next.js + RainbowKit (Wallets)
  # ----------------------------------------------------------------
  frontend:
    build: ./frontend
    container_name: poly_face
    restart: always
    environment:
      - NEXT_PUBLIC_API_URL=https://api.yourdomain.com
      - NEXT_PUBLIC_WALLET_CONNECT_ID=${WALLET_CONNECT_ID} # Get free from Reown
    ports:
      - "3000:3000"
    networks:
      - poly_net

  # ----------------------------------------------------------------
  # 5. DATA LAYER
  # ----------------------------------------------------------------
  db:
    image: postgres:15-alpine
    container_name: poly_db
    restart: always
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=polymarket_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - poly_net

  redis:
    image: redis:7-alpine
    container_name: poly_cache
    restart: always
    volumes:
      - redis_data:/data
    networks:
      - poly_net

  nginx_proxy:
    image: jc21/nginx-proxy-manager:latest
    container_name: nginx_proxy
    restart: always
    ports:
      - "80:80"
      - "81:81"
      - "443:443"
    volumes:
      - ./nginx/data:/data
      - ./nginx/letsencrypt:/etc/letsencrypt
    networks:
      - poly_net

volumes:
  postgres_data:
  redis_data:
  ollama_data:

networks:
  poly_net:
    driver: bridge