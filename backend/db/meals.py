from datetime import date
from typing import List

from db.connection import get_cursor
from models.schemas import CalculatedItem


def save_meal(raw_text: str, items: List[CalculatedItem], user_id: int = 1) -> int:
    with get_cursor() as cur:
        cur.execute(
            "INSERT INTO meals (user_id, raw_text) VALUES (%s, %s) RETURNING id",
            (user_id, raw_text),
        )
        meal_id = cur.fetchone()["id"]

        for item in items:
            cur.execute(
                """
                INSERT INTO meal_items
                    (meal_id, raw_name, canonical_name, grams, calories,
                     protein_g, carbs_g, fat_g, fdc_id, match_confidence)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    meal_id,
                    item.raw_name,
                    item.canonical_name,
                    item.grams,
                    item.calories,
                    item.protein_g,
                    item.carbs_g,
                    item.fat_g,
                    item.nutrition.fdc_id if item.nutrition else None,
                    item.nutrition.match_confidence if item.nutrition else None,
                ),
            )

        return meal_id
    
    
def delete_meal(meal_id: int, user_id: int = 1) -> bool:
    with get_cursor() as cur:
        cur.execute(
            "DELETE FROM meals WHERE id = %s AND user_id = %s",
            (meal_id, user_id),
        )
        return cur.rowcount > 0
    

def get_todays_totals(user_id: int = 1) -> dict:
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT
                COALESCE(SUM(mi.calories), 0) AS calories,
                COALESCE(SUM(mi.protein_g), 0) AS protein_g,
                COALESCE(SUM(mi.carbs_g), 0) AS carbs_g,
                COALESCE(SUM(mi.fat_g), 0) AS fat_g
            FROM meal_items mi
            JOIN meals m ON m.id = mi.meal_id
            WHERE m.user_id = %s AND m.logged_at::date = %s
            """,
            (user_id, date.today()),
        )
        return cur.fetchone()


def get_todays_log(user_id: int = 1) -> List[dict]:
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT m.id AS meal_id, m.raw_text, m.logged_at,
                   mi.raw_name, mi.canonical_name, mi.grams,
                   mi.calories, mi.protein_g, mi.carbs_g, mi.fat_g
            FROM meals m
            JOIN meal_items mi ON mi.meal_id = m.id
            WHERE m.user_id = %s AND m.logged_at::date = %s
            ORDER BY m.logged_at DESC
            """,
            (user_id, date.today()),
        )
        return cur.fetchall()