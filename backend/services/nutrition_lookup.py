# Given a food name, find real nutrition data for it via USDA FoodData Central.

import requests
from rapidfuzz import fuzz, utils
from typing import List, Optional, Tuple

from config import USDA_API_KEY
from models.schemas import NutritionData
from services.ai_matcher import select_best_match

BASE_URL = "https://api.nal.usda.gov/fdc/v1"

NUTRIENT_NAMES = {
    "calories": ["Energy", "Energy (Atwater General Factors)", "Energy (Atwater Specific Factors)"],
    "protein": ["Protein"],
    "fat": ["Total lipid (fat)"],
    "carbs": ["Carbohydrate, by difference"],
}

# USDA sometimes lists a nutrient more than once with different units
# (e.g. Energy in both KCAL and kJ). Pin the unit we actually want so we
# don't silently grab the wrong one.
NUTRIENT_UNITS = {
    "calories": "KCAL",
    "protein": "G",
    "fat": "G",
    "carbs": "G",
}


# Raise page_size to consider more USDA results per search.
def _search_usda(query: str, page_size: int = 30) -> List[dict]:
    try:
        response = requests.get(
            f"{BASE_URL}/foods/search",
            params={
                "api_key": USDA_API_KEY,
                "query": query,
                "pageSize": page_size,
                "dataType": ["Foundation", "SR Legacy"],
            },
            timeout=10,
        )
        response.raise_for_status()

        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type:
            print(f"    -> USDA returned unexpected content-type '{content_type}' (likely an outage), treating as no results")
            return []

        return response.json().get("foods", [])

    except requests.exceptions.RequestException as e:
        print(f"    -> USDA search failed: {e}")
        return []


def _extract_nutrient(food: dict, nutrient_key: str) -> Optional[float]:
    names = NUTRIENT_NAMES[nutrient_key]
    expected_unit = NUTRIENT_UNITS[nutrient_key]
    entries = food.get("foodNutrients", [])

    # Preferred: name AND unit match, so e.g. Energy(kJ) doesn't get
    # picked up in place of Energy(KCAL).
    for name in names:
        for entry in entries:
            if entry.get("nutrientName") == name and entry.get("unitName", "").upper() == expected_unit:
                return entry.get("value")

    # Fallback: name matches but unit is missing/unexpected. Rare, but
    # better to return something than nothing.
    for name in names:
        for entry in entries:
            if entry.get("nutrientName") == name:
                return entry.get("value")

    return None


def _to_nutrition_data(food: dict, confidence: float, verbose: bool = False) -> Optional[NutritionData]:
    calories = _extract_nutrient(food, "calories")
    protein = _extract_nutrient(food, "protein")
    fat = _extract_nutrient(food, "fat")
    carbs = _extract_nutrient(food, "carbs")

    missing = [n for n, v in {"calories": calories, "protein": protein, "fat": fat, "carbs": carbs}.items() if v is None]
    if missing:
        if verbose:
            print(f"    -> SKIPPED '{food.get('description')}' [{food.get('dataType')}]: missing {missing}")
        return None

    return NutritionData(
        fdc_id=food["fdcId"],
        matched_description=food.get("description", ""),
        match_confidence=confidence,
        calories_per_100g=max(0.0, calories),
        protein_g_per_100g=max(0.0, protein),
        carbs_g_per_100g=max(0.0, carbs),
        fat_g_per_100g=max(0.0, fat),
    )


def _has_required_nutrients(food: dict) -> bool:
    return all(_extract_nutrient(food, n) is not None
               for n in ("calories", "protein", "fat", "carbs"))


def _pre_filter(query: str, foods: List[dict], limit_num: int) -> List[Tuple[float, dict]]:
    scored = []

    for food in foods:
        description = food.get("description", "")
        score = fuzz.token_sort_ratio(query, description, processor=utils.default_process)
        scored.append((score, food))

    scored.sort(key=lambda pair: pair[0], reverse=True)

    with_nutrients = [(score, food) for score, food in scored if _has_required_nutrients(food)]
    return with_nutrients[:limit_num]


def lookup_nutrition(query: str, verbose: bool = False) -> Optional[NutritionData]:
    candidates = _search_usda(query)
    if not candidates:
        return None

    filtered_candidates = _pre_filter(query, candidates, 15)

    if verbose:
        for score, food in filtered_candidates:
            print(f"{score:5.1f} | {food.get('description','')}")

    if not filtered_candidates:
        return None

    selected = select_best_match(query, filtered_candidates, verbose=verbose)
    if selected is None:
        return None

    score, food = selected
    return _to_nutrition_data(food, confidence=score, verbose=verbose)


if __name__ == "__main__":
    print("Type a food name to look up (or 'quit' to exit):")
    while True:
        query = input("> ").strip()
        if query.lower() in ("quit", "exit"):
            break
        if not query:
            continue

        result = lookup_nutrition(query, verbose=True)

        if result is None:
            print(f"No confident match found for '{query}'.")
        else:
            print(result.model_dump_json(indent=2))