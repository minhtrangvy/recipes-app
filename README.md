# recipes-app

Minimal Flask + Vue recipe book scaffold for Vercel with Neon Postgres.

## Local setup

1. Put your local database values in `.env.local`.
2. Run:

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

3. Apply the schema:

```bash
psql "$DATABASE_URL" -f api/schema.sql
```

4. Run Flask locally:

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
