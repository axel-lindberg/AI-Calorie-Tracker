import os

# config.py refuses to import without these. The unit tests never hit
# OpenAI, USDA or Postgres, so placeholder values are enough.
os.environ.setdefault("OPENAI_API_KEY", "test")
os.environ.setdefault("USDA_API_KEY", "test")
os.environ.setdefault("DATABASE_URL", "postgresql://test@localhost/test")
