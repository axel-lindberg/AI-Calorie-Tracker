# AI Calorie Tracker

An AI-powered nutrition tracking system that converts natural-language meal descriptions into structured food items and retrieves nutritional information from the USDA FoodData Central database.

## Tech stack
 
| Layer | Technology |
|---|---|
| Meal parsing & food matching | OpenAI API (`gpt-4o-mini`), structured outputs via Pydantic |
| Nutrition data | USDA FoodData Central API |
| Fuzzy pre-filtering | RapidFuzz |
| Backend API | FastAPI, Uvicorn |
| Database | PostgreSQL (via `psycopg2`), Docker |
| Frontend | Vanilla JS + Vite |
