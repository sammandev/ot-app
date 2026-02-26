.PHONY: help install dev start test lint format check fix migrate makemigrations collectstatic shell createsuperuser celery

help:
	@echo "Available commands:"
	@echo "  make install        - Install dependencies with uv"
	@echo "  make dev            - Run Django development server (Daphne ASGI)"
	@echo "  make start          - Run production server (Daphne ASGI)"
	@echo "  make test           - Run tests"
	@echo "  make lint           - Run linter (ruff check)"
	@echo "  make format         - Format code (ruff format)"
	@echo "  make check          - Run lint + format check"
	@echo "  make fix            - Auto-fix lint issues"
	@echo "  make migrate        - Apply database migrations"
	@echo "  make makemigrations - Create new migrations"
	@echo "  make collectstatic  - Collect static files"
	@echo "  make shell          - Open Django shell"
	@echo "  make createsuperuser- Create admin superuser"
	@echo "  make celery         - Start Celery worker"

install:
	uv pip install -e .

dev:
	uv run python manage.py runserver 0.0.0.0:8008

start:
	uv run daphne -b 0.0.0.0 -p 8008 --application-close-timeout 30 backend.asgi:application

test:
	uv run pytest -v

lint:
	uv run ruff check .

format:
	uv run ruff format .

check:
	uv run ruff check . && uv run ruff format --check .

fix:
	uv run ruff check --fix .

migrate:
	uv run python manage.py migrate

makemigrations:
	uv run python manage.py makemigrations

collectstatic:
	uv run python manage.py collectstatic --noinput

shell:
	uv run python manage.py shell

createsuperuser:
	uv run python manage.py createsuperuser

celery:
	uv run celery -A backend worker -l info
