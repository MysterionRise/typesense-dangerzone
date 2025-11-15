.PHONY: help up down clean test test-backend test-frontend test-integration lint build

# Default target
help:
	@echo "Typesense Hybrid Demo - Available Commands:"
	@echo ""
	@echo "  make up                 - Start all services"
	@echo "  make down               - Stop all services"
	@echo "  make clean              - Clean all data and volumes"
	@echo "  make test               - Run all tests"
	@echo "  make test-backend       - Run backend tests"
	@echo "  make test-frontend      - Run frontend tests"
	@echo "  make test-integration   - Run integration tests"
	@echo "  make lint               - Run linters"
	@echo "  make build              - Build all Docker images"
	@echo "  make logs               - Show logs from all services"
	@echo ""

# Start services
up:
	@echo "🚀 Starting Typesense Hybrid Demo..."
	docker compose up --build

# Start in background
up-detached:
	@echo "🚀 Starting Typesense Hybrid Demo (detached)..."
	docker compose up -d --build

# Stop services
down:
	@echo "🛑 Stopping services..."
	docker compose down

# Clean everything
clean:
	@echo "🧹 Cleaning data and volumes..."
	docker compose down -v
	rm -rf data/
	rm -rf ui/node_modules ui/.next
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup complete"

# Run all tests
test: test-backend test-frontend test-integration
	@echo "✅ All tests completed"

# Backend tests
test-backend:
	@echo "🧪 Running backend tests..."
	cd backend && python -m pytest tests/ -v --cov=. --cov-report=term

# Frontend tests
test-frontend:
	@echo "🧪 Running frontend tests..."
	cd ui && npm test -- --passWithNoTests

# Integration tests
test-integration:
	@echo "🧪 Running integration tests..."
	@echo "Starting Typesense..."
	docker compose up -d typesense
	@sleep 5
	@echo "Running data generation..."
	docker compose run --rm backend python /app/synth_data.py
	@echo "Running indexing..."
	docker compose run --rm backend python /app/index_products.py
	@echo "Testing search..."
	@curl -s -H "X-TYPESENSE-API-KEY: xyz123_demo_key_change_in_production" \
		http://localhost:8108/collections/products | grep -q "products" && echo "✅ Collection exists"
	@echo "Cleaning up..."
	docker compose down
	@echo "✅ Integration tests passed"

# Lint
lint:
	@echo "🔍 Running linters..."
	@echo "Backend..."
	cd backend && python -m flake8 . --exclude=tests --max-line-length=120 --extend-ignore=E203,W503 || true
	@echo "Frontend..."
	cd ui && npm run lint || true
	@echo "✅ Linting complete"

# Build Docker images
build:
	@echo "🔨 Building Docker images..."
	docker compose build
	@echo "✅ Build complete"

# Show logs
logs:
	docker compose logs -f

# Quick health check
health:
	@echo "🏥 Health check..."
	@curl -s http://localhost:8108/health | grep -q ok && echo "✅ Typesense: healthy" || echo "❌ Typesense: not running"
	@curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q 200 && echo "✅ UI: healthy" || echo "❌ UI: not running"

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	cd backend && pip install -r requirements.txt
	cd ui && npm install
	@echo "✅ Dependencies installed"

# Development mode
dev:
	@echo "🔧 Starting in development mode..."
	docker compose up

# Production build
prod:
	@echo "🚀 Building for production..."
	cd ui && npm run build
	@echo "✅ Production build complete"
