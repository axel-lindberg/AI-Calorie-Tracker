import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is missing.")

OPENAI_MODEL = "gpt-4o-mini"

USDA_API_KEY = os.getenv("USDA_API_KEY")

if not USDA_API_KEY:
    raise ValueError("USDA_API_KEY is missing.")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing.")

# Origins allowed to call the API (the Vite dev server by default).
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
).split(",")
