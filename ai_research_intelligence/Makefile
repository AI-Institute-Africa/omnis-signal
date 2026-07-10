.PHONY: help install dev test lint format clean docker-build docker-up docker-down db-init db-migrate

help:
	@echo "AI Research Intelligence Platform - Make Commands"
	@echo ""
	@echo "Development:"
	@echo "  make install          Install dependencies"
	@echo "  make dev              Run development server"
	@echo "  make worker           Run Celery worker"
	@echo "  make beat             Run Celery beat"
	@echo ""
	@echo "Testing:"
	@echo "  make test             Run tests"
	@echo "  make test-cov         Run tests with coverage"
	@echo "  make lint             Run linters"
	@echo "  make format           Format code"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build     Build Docker images"
	@echo "  make docker-up        Start Docker Compose"
	@echo "  make docker-down      Stop Docker Compose"
	@echo "  make docker-logs      View Docker logs"
	@echo ""
	@echo "Database:"
	@echo "  make db-init          Initialize database"
	@echo "  make db-migrate       Run migrations"
	@echo "  make db-shell         Open database shell"
	@echo ""
	@echo "Utility:"
	@echo "  make clean            Clean up generated files"
	@echo "  make requirements      Update requirements.txt"

install:
	pip install -r requirements.txt

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

worker:
	celery -A app.workers.celery_app worker -l info

beat:
	celery -A app.workers.celery_app beat -l info

flower:
	celery -A app.workers.celery_app flower --port=5555

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=app --cov-report=html

lint:
	flake8 app/ tests/
	mypy app/ --ignore-missing-imports

format:
	black app/ tests/
	isort app/ tests/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-clean:
	docker-compose down -v

db-init:
	python -c "from app.db import init_db; init_db()"

db-migrate:
	alembic upgrade head

db-shell:
	psql $(DATABASE_URL)

requirements:
	pip freeze > requirements.txt

.DEFAULT_GOAL := help
