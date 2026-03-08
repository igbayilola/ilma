.PHONY: help up down logs dev migrate seed import-curriculum test lint fmt

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# ---------- Docker ----------
up: ## Start all services (docker compose)
	docker compose up -d --build

down: ## Stop all services
	docker compose down

logs: ## Tail API logs
	docker compose logs -f api

# ---------- Local dev ----------
dev: ## Run API locally with uvicorn
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# ---------- Database ----------
migrate: ## Run Alembic migrations (head)
	alembic upgrade head

migrate-gen: ## Auto-generate a new migration (usage: make migrate-gen msg="add users table")
	alembic revision --autogenerate -m "$(msg)"

migrate-down: ## Downgrade one migration
	alembic downgrade -1

seed: ## Seed database with sample data
	python -m app.scripts.seed

import-curriculum: ## Import curriculum JSON (usage: make import-curriculum file=path/to.json)
	python -m app.scripts.import_curriculum $(file)

# ---------- Quality ----------
test: ## Run pytest
	pytest -x -v --tb=short

test-cov: ## Run pytest with coverage
	pytest --cov=app --cov-report=term-missing -v

lint: ## Run ruff linter
	ruff check app/ tests/

fmt: ## Auto-format with ruff
	ruff format app/ tests/
