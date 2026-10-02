from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import CORS_ORIGINS
from services.ai_parser import parse_meal_text
from services.nutrition_lookup import lookup_nutrition
from services.calculator import calculate_item
from models.schemas import MatchedItem, LogMealRequest, LogMealResponse
from db.meals import save_meal, delete_meal, get_todays_totals, get_todays_log

app = FastAPI(title="AI Calorie Tracker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)


@app.post("/meals", response_model=LogMealResponse)
def log_meal(request: LogMealRequest):
    parsed = parse_meal_text(request.text)

    if not parsed.items:
        raise HTTPException(
            status_code=422,
            detail="No food or drink items found in that description.",
        )

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
