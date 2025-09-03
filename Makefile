PY ?= python3
VENV ?= .venv
PIP := $(VENV)/bin/pip
PYTHON := $(VENV)/bin/python

.DEFAULT_GOAL := help

help:
	@echo "Common targets:"
	@echo "  make init                - create venv & install deps"
	@echo "  make precommit-install   - install pre-commit hooks"
	@echo "  make up                  - docker compose up (infra)"
	@echo "  make down                - docker compose down"
	@echo "  make test                - run tests"
	@echo "  make lint                - ruff + mypy"
	@echo "  make format              - black + ruff format"
	@echo "  make ps                  - list containers"
	@echo "  make logs                - tail infra logs"

init:
	$(PY) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt -r requirements-dev.txt
	@echo "✅ Virtualenv ready. Activate with: source $(VENV)/bin/activate"

precommit-install:
	$(VENV)/bin/pre-commit install || (echo "pre-commit not found in venv; installing..." && $(PIP) install pre-commit && $(VENV)/bin/pre-commit install)

test:
	$(VENV)/bin/pytest

lint:
	$(VENV)/bin/ruff check .
	$(VENV)/bin/mypy app

format:
	$(VENV)/bin/black .
	$(VENV)/bin/ruff format .

COMPOSE ?= docker compose
COMPOSE_FILE := deploy/docker-compose.yml

up:
	$(COMPOSE) -f $(COMPOSE_FILE) up -d

down:
	$(COMPOSE) -f $(COMPOSE_FILE) down -v

ps:
	$(COMPOSE) -f $(COMPOSE_FILE) ps

logs:
	$(COMPOSE) -f $(COMPOSE_FILE) logs -f --tail=100
