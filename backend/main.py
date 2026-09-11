from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from services.ai_parser import parse_meal_text
from services.nutrition_lookup import lookup_nutrition
from services.calculator import calculate_item
from models.schemas import MatchedItem, CalculatedItem, LogMealRequest, LogMealResponse
from db.meals import save_meal, delete_meal, get_todays_totals, get_todays_log

app = FastAPI(title="AI Calorie Tracker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this before deploying
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/meals", response_model=LogMealResponse)
def log_meal(request: LogMealRequest):
    parsed = parse_meal_text(request.text)

    calculated_items = []
    for item in parsed.items:
        nutrition = lookup_nutrition(item.canonical_name)
        matched = MatchedItem(
            raw_name=item.raw_name,
            canonical_name=item.canonical_name,
            quantity=item.quantity,
            unit=item.unit,
            nutrition=nutrition,
        )
        calculated_items.append(calculate_item(matched))

    meal_id = save_meal(request.text, calculated_items)

    return LogMealResponse(meal_id=meal_id, items=calculated_items)


@app.delete("/meals/{meal_id}")
def delete_meal_endpoint(meal_id: int):
    deleted = delete_meal(meal_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Meal not found")
    return {"deleted": True, "meal_id": meal_id}


@app.get("/today/totals")
def today_totals():
    return get_todays_totals()


@app.get("/today/log")
def today_log():
    return get_todays_log()