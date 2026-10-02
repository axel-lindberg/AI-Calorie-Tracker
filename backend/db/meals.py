from datetime import datetime, timedelta
from typing import List, Tuple

from db.connection import get_cursor
from models.schemas import CalculatedItem


def _today_bounds() -> Tuple[datetime, datetime]:
    # Start/end of "today" in the server's local timezone, as aware
    # datetimes. Comparing these against the TIMESTAMPTZ column keeps the
    # day boundary correct regardless of the database's own timezone.
    start = datetime.now().astimezone().replace(hour=0, minute=0, second=0, microsecond=0)
    return start, start + timedelta(days=1)


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
    start, end = _today_bounds()
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT
                COALESCE(SUM(mi.calories), 0) AS calories,
                COALESCE(SUM(mi.protein_g), 0) AS protein_g,
                COALESCE(SUM(mi.carbs_g), 0) AS carbs_g,
                COALESCE(SUM(mi.fat_g), 0) AS fat_g,
                COUNT(*) FILTER (WHERE mi.calories IS NULL) AS unmatched_items
            FROM meal_items mi
            JOIN meals m ON m.id = mi.meal_id
            WHERE m.user_id = %s AND m.logged_at >= %s AND m.logged_at < %s
            """,
            (user_id, start, end),
        )
        return cur.fetchone()


def get_todays_log(user_id: int = 1) -> List[dict]:
    start, end = _today_bounds()
    with get_cursor() as cur:
        # LEFT JOIN so a meal is still listed (and deletable) even if it
        # somehow ended up with no items.
        cur.execute(
            """
            SELECT m.id AS meal_id, m.raw_text, m.logged_at,
                   mi.raw_name, mi.canonical_name, mi.grams,
                   mi.calories, mi.protein_g, mi.carbs_g, mi.fat_g
            FROM meals m
            LEFT JOIN meal_items mi ON mi.meal_id = m.id
            WHERE m.user_id = %s AND m.logged_at >= %s AND m.logged_at < %s
            ORDER BY m.logged_at DESC, mi.id
            """,
            (user_id, start, end),
        )
        return cur.fetchall()
