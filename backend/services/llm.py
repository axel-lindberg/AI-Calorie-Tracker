# Shared OpenAI client, so every service reuses one connection pool.

from openai import OpenAI

from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)
