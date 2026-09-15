from datetime import datetime
from fastapi import APIRouter, Query
from services.catalog import (
    MEAL_SLOTS, RECIPE_CATEGORIES, DISH_TYPES, RECIPE_TAGS, CUISINES,
    GROCERY_CATEGORIES, GRAIN_COOK, MEASURES, OVEN_TEMPS, STORAGE_TIPS,
    INGREDIENT_SWAPS, TEMPLATES, current_season_products, CHEAPER_SWAPS,
)

router = APIRouter(prefix="/api/guides", tags=["guides"])


@router.get("")
def guides(month: int | None = Query(None)):
    month = month or datetime.now().month
    return {
        "meal_slots": MEAL_SLOTS,
        "categories": RECIPE_CATEGORIES,
        "dish_types": DISH_TYPES,
        "tags": RECIPE_TAGS,
        "cuisines": CUISINES,
        "grocery": GROCERY_CATEGORIES,
        "templates": {k: v["label"] for k, v in TEMPLATES.items()},
        "grains": GRAIN_COOK,
        "measures": MEASURES,
        "oven": OVEN_TEMPS,
        "storage": STORAGE_TIPS,
        "swaps": INGREDIENT_SWAPS,
        "cheaper": CHEAPER_SWAPS,
        "season": {"month": month, "products": current_season_products(month)},
    }


@router.get("/convert")
def convert(grams: float | None = None, fahrenheit: float | None = None, celsius: float | None = None, product: str = "мука"):
    densities = {"мука": 0.54, "сахар": 0.85, "рис": 0.75, "вода": 1.0, "масло": 0.91}
    dens = densities.get(product.lower(), 0.7)
    result = {}
    if grams is not None:
        result["cups"] = round(grams / (240 * dens), 2)
        result["tbsp"] = round(grams / (15 * dens), 1)
        result["tsp"] = round(grams / (5 * dens), 1)
    if fahrenheit is not None:
        result["celsius"] = round((fahrenheit - 32) * 5 / 9, 1)
    if celsius is not None:
        result["fahrenheit"] = round(celsius * 9 / 5 + 32, 1)
    return result
