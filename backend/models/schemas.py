# Data shapes shared across the pipeline.

from pydantic import BaseModel, Field
from typing import List, Optional

class FoodItem(BaseModel):
    raw_name: str = Field(description="The food name as mentioned by the user")

    canonical_name: str = Field(
        description=(
            "A generic, canonical form of this food suitable for looking up "
            "in a nutrition database. Prefer common generic names over brand "
            "names unless the user specified a brand."
        )
    )

    quantity: float = Field(description="Numeric quantity, e.g. 2, 1, 0.5")
    unit: str = Field(
        description=(
            "Unit for the quantity, e.g. 'large', 'slice', 'cup', 'g', 'piece'. "
            "If the user gave no unit, use 'serving'."
        )
    )
    
class FoodMatchSelection(BaseModel):
    selected_fdc_id: Optional[int] = Field(
        description="fdcId of the candidate that is truly the same food as "
        "the query, or null if none of the candidates qualify."
    )
    reasoning: str = Field(description="One brief sentence explaining the choice.")


class ParsedMeal(BaseModel):
    items: List[FoodItem]
    
class NutritionData(BaseModel):
    # Nutrient values for a matched food, always per 100g.
 
    fdc_id: int
    matched_description: str  # the actual USDA food name we matched to
    match_confidence: float  # 0-100 fuzzy match score, for debugging/thresholding
 
    calories_per_100g: float
    protein_g_per_100g: float
    carbs_g_per_100g: float
    fat_g_per_100g: float
    
class MatchedItem(BaseModel):
    raw_name: str #input from user
    canonical_name: str #canonical form of user input
    quantity: float
    unit: str
    nutrition: Optional[NutritionData] = None
    

class GramEstimate(BaseModel):
    grams: float = Field(description="Estimated weight in grams for this quantity/unit of this specific food.")
    reasoning: str = Field(description="One brief sentence explaining the estimate.")
    
class DensityEstimate(BaseModel):
    grams_per_100ml: float = Field(
        description="Estimated density of this food in grams per 100ml, "
        "accounting for whether it's a dry/granular food, a liquid, or "
        "something in between."
    )
    reasoning: str = Field(description="One brief sentence explaining the estimate.")

class CalculatedItem(BaseModel):
    raw_name: str
    canonical_name: str
    grams: Optional[float] = None
    calories: Optional[float] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None
    nutrition: Optional[NutritionData] = None


class LogMealRequest(BaseModel):
    text: str

class LogMealResponse(BaseModel):
    meal_id: int
    items: List[CalculatedItem]