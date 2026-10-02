# Convert a matched item's quantity/unit into grams, then scale its
# per-100g nutrition data to the actual amount consumed.

from typing import Optional

from config import OPENAI_MODEL
from models.schemas import MatchedItem, CalculatedItem, GramEstimate, DensityEstimate
from services.llm import client

SYSTEM_PROMPT = """\
You are estimating the weight, in grams, of a quantity of food.

You will be given a food name, a quantity, and a unit (e.g. "2 large" for \
eggs, "1 slice" for bread, "1 cup" for rice). Estimate the total weight in \
grams that this quantity/unit represents for this specific food, using \
typical real-world serving sizes.

Be specific to the food: a "slice" of bread and a "slice" of pizza are not \
the same weight, and a "cup" of leafy greens and a "cup" of rice are not \
the same weight either.
"""

# Units we can convert without an LLM call.
_DIRECT_GRAMS = {
    "g": 1.0,
    "gram": 1.0,
    "grams": 1.0,
    "kg": 1000.0,
    "kilogram": 1000.0,
    "kilograms": 1000.0,
    "oz": 28.35,
    "ounce": 28.35,
    "ounces": 28.35,
    "lb": 453.6,
    "lbs": 453.6,
    "pound": 453.6,
    "pounds": 453.6,
}

_VOLUME_TO_ML = {
    "ml": 1.0,
    "milliliter": 1.0,
    "milliliters": 1.0,
    "cl": 10.0,
    "centiliter": 10.0,
    "centiliters": 10.0,
    "dl": 100.0,
    "deciliter": 100.0,
    "deciliters": 100.0,
    "l": 1000.0,
    "liter": 1000.0,
    "liters": 1000.0,
    "tsp": 5.0,
    "teaspoon": 5.0,
    "teaspoons": 5.0,
    "tbsp": 15.0,
    "tablespoon": 15.0,
    "tablespoons": 15.0,
    "cup": 240.0,
    "cups": 240.0,
    "fl oz": 30.0,
    "fl. oz": 30.0,
    "fluid ounce": 30.0,
    "fluid ounces": 30.0,
}

DENSITY_SYSTEM_PROMPT = """\
You are estimating the density of a food, in grams per 100ml of volume.

Consider whether this food is dry and granular (e.g. rolled oats, flour, \
rice - much lighter than water, often 30-60g per 100ml), a liquid (close \
to 100g per 100ml, like milk or juice), or something denser/chunkier. Do \
not default to water-like density unless the food is actually a liquid.
"""


def estimate_density_g_per_100ml(canonical_name: str) -> Optional[float]:
    completion = client.beta.chat.completions.parse(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": DENSITY_SYSTEM_PROMPT},
            {"role": "user", "content": f'Food: "{canonical_name}"'},
        ],
        response_format=DensityEstimate,
    )
    result = completion.choices[0].message.parsed
    if result is None or result.grams_per_100ml <= 0:
        return None
    return result.grams_per_100ml


def estimate_grams(canonical_name: str, quantity: float, unit: str, verbose: bool = False) -> Optional[float]:
    unit_key = unit.strip().lower()

    direct_factor = _DIRECT_GRAMS.get(unit_key)
    if direct_factor is not None:
        return quantity * direct_factor

    volume_factor = _VOLUME_TO_ML.get(unit_key)
    if volume_factor is not None:
        total_ml = quantity * volume_factor
        density = estimate_density_g_per_100ml(canonical_name)
        if density is None:
            if verbose:
                print(f"    -> no density estimate for '{canonical_name}'")
            return None
        grams = total_ml * (density / 100.0)
        if verbose:
            print(f"    -> {total_ml:.0f}ml @ {density:.0f}g/100ml = {grams:.1f}g for '{canonical_name}'")
        return grams

    completion = client.beta.chat.completions.parse(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f'Food: "{canonical_name}"\nQuantity: {quantity}\nUnit: "{unit}"',
            },
        ],
        response_format=GramEstimate,
    )

    result = completion.choices[0].message.parsed

    if result is None or result.grams <= 0:
        if verbose:
            print(f"    -> LLM gave no usable gram estimate for '{canonical_name}' ({quantity} {unit})")
        return None

    if verbose:
        print(f"    -> estimated {result.grams:.1f}g for '{canonical_name}' ({quantity} {unit}): {result.reasoning}")

    return result.grams


def calculate_item(item: MatchedItem, verbose: bool = False) -> CalculatedItem:
    if item.nutrition is None:
        return CalculatedItem(raw_name=item.raw_name, canonical_name=item.canonical_name)

    grams = estimate_grams(item.canonical_name, item.quantity, item.unit, verbose=verbose)
    if grams is None:
        return CalculatedItem(
            raw_name=item.raw_name,
            canonical_name=item.canonical_name,
            nutrition=item.nutrition,
        )

    factor = grams / 100.0
    n = item.nutrition

    return CalculatedItem(
        raw_name=item.raw_name,
        canonical_name=item.canonical_name,
        grams=grams,
        calories=n.calories_per_100g * factor,
        protein_g=n.protein_g_per_100g * factor,
        carbs_g=n.carbs_g_per_100g * factor,
        fat_g=n.fat_g_per_100g * factor,
        nutrition=n,
    )


if __name__ == "__main__":
    from models.schemas import NutritionData

    print("Type: <canonical_name>, <quantity>, <unit> (or 'quit' to exit):")
    while True:
        line = input("> ").strip()
        if line.lower() in ("quit", "exit"):
            break
        if not line:
            continue

        try:
            name, qty, unit = [p.strip() for p in line.split(",")]
            grams = estimate_grams(name, float(qty), unit, verbose=True)
            print(f"-> {grams}g" if grams else "-> could not estimate")
        except ValueError:
            print("format: canonical_name, quantity, unit")