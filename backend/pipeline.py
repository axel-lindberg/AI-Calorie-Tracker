# Interactive CLI that runs the full parse -> lookup -> calculate pipeline
# without the API or database. Handy for manually checking matches.

import json
from typing import List

from services.ai_parser import parse_meal_text
from services.nutrition_lookup import lookup_nutrition
from services.calculator import calculate_item
from models.schemas import MatchedItem, CalculatedItem


def parse_and_lookup(text: str, verbose: bool = True) -> List[CalculatedItem]:
    parsed = parse_meal_text(text)

    results = []
    for item in parsed.items:
        nutrition = lookup_nutrition(item.canonical_name, verbose=verbose)

        matched = MatchedItem(
            raw_name=item.raw_name,
            canonical_name=item.canonical_name,
            quantity=item.quantity,
            unit=item.unit,
            nutrition=nutrition,
        )

        results.append(calculate_item(matched, verbose=verbose))

    return results


if __name__ == "__main__":
    print("Describe a meal (or 'quit' to exit):")
    while True:
        text = input("> ").strip()
        if text.lower() in ("quit", "exit"):
            break
        if not text:
            continue

        results = parse_and_lookup(text, verbose=True)
        print(json.dumps([r.model_dump() for r in results], indent=2))

        for r in results:
            if r.nutrition is not None:
                n = r.nutrition
                print(
                    f"  per 100g [{n.matched_description}]: "
                    f"{n.calories_per_100g:.1f} kcal, "
                    f"{n.protein_g_per_100g:.1f}g protein, "
                    f"{n.carbs_g_per_100g:.1f}g carbs, "
                    f"{n.fat_g_per_100g:.1f}g fat"
                )
            if r.calories is None:
                print(f"could not calculate nutrition for '{r.raw_name}' ({r.canonical_name})")