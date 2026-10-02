# AI Calorie Tracker

An AI-powered nutrition tracking system that converts natural-language meal descriptions into structured food items and retrieves nutritional information from the USDA FoodData Central database.

## How it works

1. **Parse**: an LLM splits free text ("two eggs and a slice of toast") into food items, each with a quantity and unit.
2. **Look up**: each item is searched in USDA FoodData Central. Results are pre-filtered with RapidFuzz, then an LLM picks the candidate that is actually the same food, or rejects them all.
3. **Calculate**: the quantity is converted to grams (directly for weight units, via an estimated density for volume units, otherwise by LLM estimate) and the per-100 g nutrient values are scaled to match.
4. **Store**: the meal and its items are saved in PostgreSQL, and the frontend shows today's log and totals.

## Tech stack

| Layer | Technology |
|---|---|
| Meal parsing & food matching | OpenAI API (`gpt-4o-mini`), structured outputs via Pydantic |
| Nutrition data | USDA FoodData Central API |
| Fuzzy pre-filtering | RapidFuzz |
| Backend API | FastAPI, Uvicorn |
| Database | PostgreSQL (via `psycopg2`), Docker |
| Frontend | Vanilla JS + Vite |

## Getting started

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker
- An [OpenAI API key](https://platform.openai.com/api-keys) and a free [USDA FoodData Central API key](https://fdc.nal.usda.gov/api-key-signup)

### 1. Configure environment

```bash
cp .env.example .env                    # fill in API keys and database credentials
cp frontend/.env.example frontend/.env
```

### 2. Start the database

```bash
docker compose up -d
```

The schema in `backend/db/schema.sql` is applied automatically the first time the container starts with an empty volume. To apply it to an existing database instead:

```bash
docker compose exec -T db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < backend/db/schema.sql
```

### 3. Run the backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

The API runs on http://localhost:8000. Interactive docs are at `/docs`.

### 4. Run the frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173.

## API

| Method | Path | Description |
|---|---|---|
| `POST` | `/meals` | Log a meal from `{"text": "..."}` |
| `DELETE` | `/meals/{meal_id}` | Delete a logged meal |
| `GET` | `/today/totals` | Today's calorie and macro totals |
| `GET` | `/today/log` | Today's meals and their items |

## Development

Run the unit tests (no API keys or database needed):

```bash
cd backend
pip install -r requirements-dev.txt
pytest
```

Each pipeline stage can also be tried interactively from `backend/`:

```bash
python pipeline.py                     # full parse -> lookup -> calculate
python -m services.ai_parser           # parsing only
python -m services.nutrition_lookup    # USDA lookup only
python -m services.calculator          # gram estimation only
```

## Project structure

```
backend/
  main.py            FastAPI app and routes
  config.py          Environment configuration
  pipeline.py        Interactive CLI for the full pipeline
  services/          Parsing, USDA lookup, matching and gram calculation
  models/schemas.py  Pydantic models shared across the pipeline
  db/                Schema and database access
  tests/             Unit tests
frontend/
  index.html
  src/               API client, state store and render modules
```
