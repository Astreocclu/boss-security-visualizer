.PHONY: help install install-dev clean test test-backend test-frontend test-e2e lint format check security build run migrate collectstatic docker-build docker-run

# Default target
help:
	@echo "Available commands:"
	@echo "  install          Install production dependencies"
	@echo "  install-dev      Install development dependencies"
	@echo "  clean            Clean build artifacts and cache"
	@echo "  test             Run all tests"
	@echo "  test-backend     Run backend tests"
	@echo "  test-frontend    Run frontend tests"
	@echo "  test-e2e         Run end-to-end tests"
	@echo "  lint             Run linting checks"
	@echo "  format           Format code"
	@echo "  check            Run all quality checks"
	@echo "  security         Run security checks"
	@echo "  build            Build the application"
	@echo "  run              Run development server"
	@echo "  migrate          Run database migrations"
	@echo "  collectstatic    Collect static files"
	@echo "  docker-build     Build Docker image"
	@echo "  docker-run       Run with Docker Compose"

# Installation
install:
	pip install -r requirements.txt
	cd frontend && npm ci

install-dev:
	pip install -r requirements-dev.txt
	cd frontend && npm install
	pre-commit install

# Cleaning
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	cd frontend && rm -rf build/ node_modules/.cache/

# Testing
test: test-backend test-frontend

test-backend:
	python -m pytest --cov=api --cov-report=term-missing --cov-report=html

test-frontend:
	cd frontend && npm run test:unit:coverage

test-e2e:
	cd frontend && npm run test:e2e

# Code quality
lint:
	flake8 .
	pylint api/
	mypy .
	cd frontend && npm run lint

format:
	black .
	isort .
	cd frontend && npm run format

check: lint test security
	python manage.py check
	python manage.py makemigrations --check --dry-run

security:
	bandit -r api/
	safety check
	cd frontend && npm audit

# Build and run
build:
	cd frontend && npm run build:prod
	python manage.py collectstatic --noinput

run:
	python manage.py runserver &
	cd frontend && npm start

# Django management
migrate:
	python manage.py migrate

collectstatic:
	python manage.py collectstatic --noinput

createsuperuser:
	python manage.py createsuperuser

# Docker
docker-build:
	docker build -t homescreen:latest .

docker-run:
	docker-compose up --build

docker-run-dev:
	docker-compose -f docker-compose.dev.yml up --build

docker-stop:
	docker-compose down

docker-clean:
	docker-compose down -v
	docker system prune -f

# Database
db-reset:
	python manage.py flush --noinput
	python manage.py migrate

db-seed:
	python manage.py loaddata fixtures/initial_data.json

# Deployment
deploy-staging:
	@echo "Deploying to staging..."
	# Add staging deployment commands here

deploy-prod:
	@echo "Deploying to production..."
	# Add production deployment commands here

# Development utilities
shell:
	python manage.py shell

dbshell:
	python manage.py dbshell

logs:
	tail -f logs/*.log

# CI/CD helpers
ci-install:
	pip install -r requirements-dev.txt
	cd frontend && npm ci

ci-test:
	python -m pytest --cov=api --cov-report=xml
	cd frontend && npm run test:unit:coverage

ci-build:
	cd frontend && npm run build:prod
	python manage.py collectstatic --noinput --clear

# Documentation
docs:
	cd docs && make html

docs-serve:
	cd docs/_build/html && python -m http.server 8080
