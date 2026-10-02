from services.nutrition_lookup import _extract_nutrient, _pre_filter, _to_nutrition_data


def _food(nutrients, description="Egg, whole, raw", fdc_id=1):
    return {
        "fdcId": fdc_id,
        "description": description,
        "foodNutrients": [
            {"nutrientName": name, "unitName": unit, "value": value}
            for name, unit, value in nutrients
        ],
    }


COMPLETE = [
    ("Energy", "KCAL", 143),
    ("Protein", "G", 12.6),
    ("Total lipid (fat)", "G", 9.5),
    ("Carbohydrate, by difference", "G", 0.7),
]


def test_extract_nutrient_prefers_kcal_over_kj():
    food = _food([("Energy", "kJ", 598), ("Energy", "KCAL", 143)])
    assert _extract_nutrient(food, "calories") == 143


def test_extract_nutrient_falls_back_when_unit_differs():
    food = _food([("Protein", "MG", 12.6)])
    assert _extract_nutrient(food, "protein") == 12.6


def test_extract_nutrient_missing_returns_none():
    assert _extract_nutrient(_food([]), "fat") is None


def test_to_nutrition_data_clamps_negative_values():
    nutrients = COMPLETE[:-1] + [("Carbohydrate, by difference", "G", -0.3)]
    data = _to_nutrition_data(_food(nutrients), confidence=80.0)
    assert data.carbs_g_per_100g == 0.0
    assert data.calories_per_100g == 143


def test_to_nutrition_data_rejects_incomplete_food():
    assert _to_nutrition_data(_food(COMPLETE[:2]), confidence=80.0) is None


def test_pre_filter_ranks_by_similarity_and_drops_incomplete():
    foods = [
        _food(COMPLETE, description="Eggnog", fdc_id=1),
        _food(COMPLETE, description="Egg, whole, raw", fdc_id=2),
        _food(COMPLETE[:1], description="Egg, whole", fdc_id=3),
    ]

    result = _pre_filter("egg whole raw", foods, limit_num=5)

    assert [food["fdcId"] for _, food in result] == [2, 1]
