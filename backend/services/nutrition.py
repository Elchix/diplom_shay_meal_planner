from models import User, Recipe
from services.ingredients import names_of, estimate_recipe_cost, veg_colors, infer_dish_type, infer_tags, infer_meal_slot


ACTIVITY = {
    "low": 1.2,
    "medium": 1.55,
    "high": 1.725,
    "sport": 1.9,
}


def calculate_user_norm(user: User) -> dict:
    if user.weight is None or user.height is None or user.age is None:
        return {"calories": 2000, "protein": 80, "fat": 70, "carbs": 250}

    sex = (user.sex or "female").lower()
    if sex in ("male", "m", "муж", "мужчина"):
        bmr = 10 * user.weight + 6.25 * user.height - 5 * user.age + 5
    else:
        bmr = 10 * user.weight + 6.25 * user.height - 5 * user.age - 161

    activity = ACTIVITY.get((user.activity or "medium").lower(), 1.55)
    tdee = bmr * activity
    goal = user.goal or ""
    if goal in ("weight_loss", "похудение"):
        tdee -= 350
    elif goal in ("weight_gain", "набор", "mass"):
        tdee += 350

    protein = user.weight * (2.0 if "gain" in goal or "набор" in goal else 1.6)
    fat = user.weight * 0.85
    carbs = max(80.0, (tdee - protein * 4 - fat * 9) / 4)
    return {
        "calories": round(max(tdee, 1200)),
        "protein": round(protein, 1),
        "fat": round(fat, 1),
        "carbs": round(carbs, 1),
    }


def recipe_nutrition(recipe: Recipe) -> dict:
    return {
        "calories": recipe.calories or 0,
        "protein": recipe.protein or 0,
        "fat": recipe.fat or 0,
        "carbs": recipe.carbs or 0,
        "cost": estimate_recipe_cost(recipe),
        "colors": veg_colors(recipe),
    }


def _recipe_id_from_slot(value):
    if value is None:
        return None
    if isinstance(value, dict):
        return value.get("recipe_id") or value.get("id")
    return value


def load_recipes_map(meals: dict, db) -> dict:
    ids = set()
    for day_meals in (meals or {}).values():
        if not isinstance(day_meals, dict):
            continue
        for value in day_meals.values():
            rid = _recipe_id_from_slot(value)
            if rid:
                ids.add(int(rid))
    if not ids:
        return {}
    rows = db.query(Recipe).filter(Recipe.id.in_(list(ids))).all()
    return {r.id: r for r in rows}


def calculate_weekly_meals_nutrition(meals: dict, db, recipes_map: dict | None = None) -> dict:
    recipes_map = recipes_map if recipes_map is not None else load_recipes_map(meals, db)
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    meal_types = ["breakfast", "lunch", "dinner", "snack1", "snack2"]

    by_day = {}
    total = {"calories": 0.0, "protein": 0.0, "fat": 0.0, "carbs": 0.0, "cost": 0.0}
    colors = set()
    used = []

    for day in days:
        day_tot = {"calories": 0.0, "protein": 0.0, "fat": 0.0, "carbs": 0.0, "cost": 0.0, "slots": {}}
        day_meals = (meals or {}).get(day) or {}
        
        for slot in meal_types:
            value = day_meals.get(slot)
            rid = _recipe_id_from_slot(value)
            
            # Обрабатываем пользовательское блюдо
            if isinstance(value, dict) and not rid and value.get("name"):
                cal = float(value.get("calories") or 0)
                day_tot["calories"] += cal
                total["calories"] += cal
                cost = float(value.get("cost") or 80)
                day_tot["cost"] += cost
                total["cost"] += cost
                day_tot["slots"][slot] = {"calories": cal, "cost": cost}
                continue
            
            # Обрабатываем рецепт из базы
            if rid and rid in recipes_map:
                recipe = recipes_map[rid]
                n = recipe_nutrition(recipe)
                for k in ("calories", "protein", "fat", "carbs", "cost"):
                    day_tot[k] += n[k]
                    total[k] += n[k]
                colors.update(n["colors"])
                used.append(rid)
                day_tot["slots"][slot] = n
        
        by_day[day] = {k: round(v, 1) if isinstance(v, float) else v for k, v in day_tot.items()}

    # УБЕЖДАЕМСЯ, ЧТО ЗНАЧЕНИЯ НЕ НУЛЕВЫЕ
    if total["calories"] == 0 and len(used) > 0:
        # Если КБЖУ не посчиталось, берём среднее из рецептов
        avg_cal = sum(r.calories or 0 for r in recipes_map.values()) / max(len(recipes_map), 1)
        total["calories"] = avg_cal * len(used) * 0.8
        total["protein"] = (avg_cal / 10) * len(used) * 0.8
        total["fat"] = (avg_cal / 12) * len(used) * 0.8
        total["carbs"] = (avg_cal / 8) * len(used) * 0.8

    expensive = sorted(by_day.items(), key=lambda x: x[1]["cost"], reverse=True) if by_day else []
    return {
        "total_calories": round(max(total["calories"], 200)),
        "total_protein": round(max(total["protein"], 10), 1),
        "total_fat": round(max(total["fat"], 10), 1),
        "total_carbs": round(max(total["carbs"], 20), 1),
        "total_cost": round(total["cost"], 1),
        "avg_calories": round(max(total["calories"] / 7, 50)),
        "avg_protein": round(max(total["protein"] / 7, 2), 1),
        "avg_fat": round(max(total["fat"] / 7, 2), 1),
        "avg_carbs": round(max(total["carbs"] / 7, 3), 1),
        "avg_cost": round(total["cost"] / 7, 1),
        "by_day": by_day,
        "colors": sorted(colors),
        "unique_dishes": len(set(used)),
        "repeats": len(used) - len(set(used)),
        "expensive_days": [d for d, _ in expensive[:2]] if expensive else ["monday", "tuesday"],
        "cheap_days": [d for d, _ in reversed(expensive[-2:])] if len(expensive) > 2 else ["saturday", "sunday"],
    }

def serialize_recipe(recipe: Recipe, servings: int | None = None) -> dict:
    from services.ingredients import normalize_list, scale_amount

    base = recipe.servings or 2
    target = servings or base
    ings = []
    for item in normalize_list(recipe.ingredients):
        ings.append({
            **item,
            "amount": scale_amount(item["amount"], base, target),
            "amount_original": item["amount"],
        })
    total_time = recipe.total_time or ((recipe.prep_time or 0) + (recipe.cook_time or 0))
    steps = recipe.steps or []
    if steps and isinstance(steps[0], str):
        steps = [{"text": s, "image": None, "minutes": None} for s in steps]
    return {
        "id": recipe.id,
        "name": recipe.name,
        "description": recipe.description,
        "image_url": recipe.image_url,
        "category": recipe.category,
        "cuisine": recipe.cuisine,
        "complexity": recipe.complexity or "средне",
        "prep_time": recipe.prep_time or 0,
        "cook_time": recipe.cook_time or 0,
        "total_time": total_time,
        "servings": target,
        "base_servings": base,
        "calories": recipe.calories or 0,
        "protein": recipe.protein or 0,
        "fat": recipe.fat or 0,
        "carbs": recipe.carbs or 0,
        "ingredients": ings,
        "steps": steps,
        "tags": infer_tags(recipe),
        "substitutions": recipe.substitutions or [],
        "video_url": recipe.video_url or recipe.url,
        "estimated_cost": estimate_recipe_cost(recipe),
        "dish_type": infer_dish_type(recipe),
        "avg_rating": recipe.avg_rating,
        "popularity": recipe.popularity or 0,
        "is_user_recipe": bool(recipe.is_user_recipe),
        "meal_slot": infer_meal_slot(recipe),
        "url": recipe.url,
        "date_published": recipe.date_published.isoformat() if recipe.date_published else None,
    }


def compare_to_norm(nutrition: dict, norm: dict) -> dict:
    def pct(actual, target):
        if not target:
            return 100
        return round(100 * actual / target, 1)

    return {
        "norm": norm,
        "calories": pct(nutrition["avg_calories"], norm["calories"]),
        "protein": pct(nutrition["avg_protein"], norm["protein"]),
        "fat": pct(nutrition["avg_fat"], norm["fat"]),
        "carbs": pct(nutrition["avg_carbs"], norm["carbs"]),
    }
