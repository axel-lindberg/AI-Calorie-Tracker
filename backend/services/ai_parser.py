# Turn free-text input into structured food items.

import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL
from models.schemas import ParsedMeal

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """\
You are a nutrition-logging assistant. The user will describe what they ate \
in free text. Extract every distinct food item mentioned, with:

- raw_name: the food as the user described it
- canonical_name: a generic, brand-free name suitable for searching a \
  nutrition database (e.g. "toast" -> "bread, white, toasted", \
  "a coke" -> "cola, carbonated beverage")
- quantity: a numeric quantity (estimate a sensible default if not stated, \
  e.g. "an egg" -> 1)
- unit: the unit for that quantity (e.g. "large", "slice", "cup", "g"). \
  If nothing sensible applies, use "serving".

Do NOT convert or estimate units yourself - preserve the quantity and unit \
exactly as the user stated them, in their original unit. For example, "2dl" \
must stay as quantity=2, unit="dl" - never convert it to grams, milliliters, \
or any other unit. Downstream code handles all unit conversion and weight \
estimation; your only job here is faithful extraction.

Only extract actual food/drink items. Ignore filler words.
"""

def parse_meal_text(text: str) -> ParsedMeal:
    completion = client.beta.chat.completions.parse(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        response_format=ParsedMeal,
    )

    parsed = completion.choices[0].message.parsed

    if parsed is None:
        raise ValueError("Model did not return a parseable result.")

    return parsed


if __name__ == "__main__":
    print("Type a meal description (or 'quit' to exit):")
    while True:
        user_input = input("> ").strip()
        if user_input.lower() in ("quit", "exit"):
            break
        if not user_input:
            continue

        result = parse_meal_text(user_input)
        print(json.dumps(result.model_dump(), indent=2))