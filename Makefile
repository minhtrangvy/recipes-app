SHELL := /bin/zsh
ENV_RUN := python3 scripts/run_with_env.py .env.local

.PHONY: help setup install-backend install-frontend db-schema backend frontend

help:
	@printf "Available targets:\n"
	@printf "  make setup             Install deps and apply schema\n"
	@printf "  make install-backend   Install Python dependencies into .venv\n"
	@printf "  make install-frontend  Install web dependencies\n"
	@printf "  make db-schema         Apply api/schema.sql using values from .env.local\n"
	@printf "  make backend           Run the Flask API locally on port 5000\n"
	@printf "  make frontend          Run the Vue app locally with Vite\n"

setup: install-backend install-frontend db-schema

install-backend:
	python3 -m venv .venv
	source .venv/bin/activate && pip install -r api/requirements.txt

install-frontend:
	cd web && npm install

db-schema:
	$(ENV_RUN) psql '$$DATABASE_URL' -f api/schema.sql

backend:
	$(ENV_RUN) .venv/bin/flask --app api.index run --debug

frontend:
	cd web && npm run dev
