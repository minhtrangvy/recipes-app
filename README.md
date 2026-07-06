# recipes-app

Minimal Flask + Vue recipe book scaffold for Vercel with Neon Postgres.

## Local setup

1. Put your local database values in `.env.local`.
2. Add `OPENAI_API_KEY` if you want automatic recipe import from `inspiration_url`.
3. Run:

```bash
make setup
make backend
make frontend
```

## Backend

1. Create a virtualenv and install backend deps:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r api/requirements.txt
```

2. Set `DATABASE_URL` from `.env.example` in `.env.local`.
3. Set `OPENAI_API_KEY` in `.env.local` and Vercel if you want backend imports from recipe URLs.

4. Apply the schema:

```bash
psql "$DATABASE_URL" -f api/schema.sql
```

5. Run Flask locally:

```bash
source .venv/bin/activate
flask --app api.index run --debug
```

## Frontend

1. Install dependencies:

```bash
cd web
npm install
```

2. Run Vite:

```bash
npm run dev
```

Vite proxies `/api` requests to `http://127.0.0.1:5000`.

## Data model

- `recipes`
- `recipe_versions`
- `ingredients`

Ingredients are attached to `recipe_version_id` and currently store a minimal `name` field so the active version can be edited in the UI.

If a recipe has an `inspiration_url` and `OPENAI_API_KEY` is available, the backend can fetch the page, send the page text to OpenAI, and return an editable import preview for ingredients/instructions/steps before anything is saved into version 1.
