SHELL := /bin/zsh

.PHONY: help setup install-backend install-frontend db-schema backend frontend

help:
	@printf "Available targets:\n"
	@printf "  make setup             Install deps and apply schema\n"
	@printf "  make install-backend   Install Python dependencies into .venv\n"
	@printf "  make install-frontend  Install web dependencies\n"
	@printf "  make db-schema         Apply api/schema.sql using DATABASE_URL from .env.local\n"
	@printf "  make backend           Run the Flask API locally on port 5000\n"
	@printf "  make frontend          Run the Vue app locally with Vite\n"

setup: install-backend install-frontend db-schema

install-backend:
	python3 -m venv .venv
	source .venv/bin/activate && pip install -r api/requirements.txt

install-frontend:
	cd web && npm install

db-schema:
	set -a && source .env.local && set +a && psql "$$DATABASE_URL" -f api/schema.sql

backend:
	set -a && source .env.local && set +a && source .venv/bin/activate && flask --app api.index run --debug

frontend:
	cd web && npm run dev
