import pytest

from models.schemas import MatchedItem, NutritionData
from services import calculator


def _nutrition(**overrides):
    values = dict(
        fdc_id=1,
        matched_description="Test food",
        match_confidence=90.0,
        calories_per_100g=200.0,
        protein_g_per_100g=10.0,
        carbs_g_per_100g=20.0,
        fat_g_per_100g=5.0,
    )
    values.update(overrides)
    return NutritionData(**values)


@pytest.mark.parametrize(
    "quantity, unit, expected",
    [
        (150, "g", 150.0),
        (2, "grams", 2.0),
        (1.5, "kg", 1500.0),
        (2, " OZ ", 56.7),
        (1, "lb", 453.6),
    ],
)
def test_estimate_grams_direct_units(quantity, unit, expected):
    assert calculator.estimate_grams("rice", quantity, unit) == pytest.approx(expected)


def test_estimate_grams_volume_uses_density(monkeypatch):
    monkeypatch.setattr(calculator, "estimate_density_g_per_100ml", lambda name: 50.0)
    # 2 dl = 200 ml at 50 g/100 ml
    assert calculator.estimate_grams("rolled oats", 2, "dl") == pytest.approx(100.0)


def test_estimate_grams_volume_without_density(monkeypatch):
    monkeypatch.setattr(calculator, "estimate_density_g_per_100ml", lambda name: None)
    assert calculator.estimate_grams("rolled oats", 1, "cup") is None


def test_calculate_item_scales_per_100g_values(monkeypatch):
    monkeypatch.setattr(calculator, "estimate_grams", lambda *args, **kwargs: 150.0)
    item = MatchedItem(
        raw_name="rice", canonical_name="rice, cooked", quantity=1, unit="cup",
        nutrition=_nutrition(),
    )

    result = calculator.calculate_item(item)

    assert result.grams == 150.0
    assert result.calories == pytest.approx(300.0)
    assert result.protein_g == pytest.approx(15.0)
    assert result.carbs_g == pytest.approx(30.0)
    assert result.fat_g == pytest.approx(7.5)


def test_calculate_item_without_nutrition_has_no_values():
    item = MatchedItem(raw_name="mystery", canonical_name="mystery", quantity=1, unit="serving")

    result = calculator.calculate_item(item)

    assert result.calories is None
    assert result.grams is None
