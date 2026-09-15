from datetime import datetime, timedelta, date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models import User, WeeklyMenu, Recipe
from schemas import AutoPlanRequest, SlotAssign, MenuUpdate
from services.autoplan import AutoPlanGenerator, DAYS, DEFAULT_SLOTS
from services.slots import VALID_SLOTS, normalize_slot, normalize_day, normalize_slot_list
from services.nutrition import (
    calculate_weekly_meals_nutrition,
    calculate_user_norm,
    compare_to_norm,
    serialize_recipe,
    load_recipes_map,
)
from services.shopping import build_shopping_from_menu, replace_week_shopping, serialize_item
from auth import get_current_user

router = APIRouter(prefix="/api/menu", tags=["menu"])

SLOT_DEFAULTS = list(VALID_SLOTS)


def sanitize_meals(meals: dict | None, slots=None) -> dict:
    slots = normalize_slot_list(slots) or SLOT_DEFAULTS
    cleaned = {d: {s: None for s in slots} for d in DAYS}
    if not meals:
        return cleaned
    for day, day_slots in meals.items():
        day_key = normalize_day(day)
        if not day_key or not isinstance(day_slots, dict):
            continue
        cleaned.setdefault(day_key, {s: None for s in slots})
        for slot, value in day_slots.items():
            slot_key = normalize_slot(slot)
            if not slot_key:
                continue
            cleaned[day_key][slot_key] = value
    return cleaned

def week_bounds(start: date | None, week_starts_on: str = "monday"):
    today = start or datetime.now().date()
    if week_starts_on == "sunday":
        delta = (today.weekday() + 1) % 7
    else:
        delta = today.weekday()
    week_start = datetime.combine(today - timedelta(days=delta), datetime.min.time())
    week_end = week_start + timedelta(days=6)
    return week_start, week_end


def empty_meals(slots=None):
    slots = slots or SLOT_DEFAULTS
    return {d: {s: None for s in slots} for d in DAYS}


def enrich_menu(menu: WeeklyMenu, db, user: User):
    recipes = load_recipes_map(menu.meals, db)
    days = {}
    meals = sanitize_meals(menu.meals)
    for day, slots in meals.items():
        days[day] = {}
        if not isinstance(slots, dict):
            continue
        for slot, value in slots.items():
            if isinstance(value, dict) and not value.get("recipe_id") and value.get("name"):
                days[day][slot] = {"custom": True, **value}
            elif value:
                rid = value.get("recipe_id") if isinstance(value, dict) else value
                rec = recipes.get(int(rid)) if rid else None
                days[day][slot] = serialize_recipe(rec, user.family_size) if rec else None
            else:
                days[day][slot] = None
    nutrition = calculate_weekly_meals_nutrition(meals, db, recipes)
    norm = calculate_user_norm(user)
    return {
        "id": menu.id,
        "user_id": menu.user_id,
        "week_start": menu.week_start,
        "week_end": menu.week_end,
        "meals": meals,
        "days": days,
        "nutrition": nutrition,
        "balance": compare_to_norm(nutrition, norm),
        "template": menu.template,
        "banned": menu.banned,
        "estimated_cost": nutrition.get("total_cost") or menu.estimated_cost,
    }


def get_or_create_week(db, user, week_start=None):
    settings = user.settings or {}
    start, end = week_bounds(week_start, settings.get("week_starts_on", "monday"))
    menu = (
        db.query(WeeklyMenu)
        .filter(WeeklyMenu.user_id == user.id, WeeklyMenu.week_start == start)
        .order_by(WeeklyMenu.id.desc())
        .first()
    )
    if not menu:
        menu = WeeklyMenu(
            user_id=user.id,
            week_start=start,
            week_end=end,
            meals=sanitize_meals(None, settings.get("meal_slots") or SLOT_DEFAULTS),
        )
        db.add(menu)
        db.commit()
        db.refresh(menu)
        return menu
    repaired = sanitize_meals(menu.meals, settings.get("meal_slots") or SLOT_DEFAULTS)
    raw = menu.meals or {}
    if "string" in raw or any(isinstance(v, dict) and "string" in v for v in raw.values()):
        from sqlalchemy.orm.attributes import flag_modified
        menu.meals = repaired
        flag_modified(menu, "meals")
        db.commit()
    return menu


@router.post("/autoplan")
def autoplan(payload: AutoPlanRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    prefs = payload.model_dump(exclude_none=True, mode="json")
    prefs.pop("user_id", None)
    prefs["meal_slots"] = normalize_slot_list(prefs.get("meal_slots")) or None
    generator = AutoPlanGenerator(db, user, prefs)
    try:
        result = generator.generate(iterations=payload.iterations or 250)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    menu = get_or_create_week(db, user)
    menu.meals = sanitize_meals(result["menu"], prefs.get("meal_slots") or SLOT_DEFAULTS)
    menu.template = payload.template
    n = result["nutrition"]
    menu.total_calories = n.get("total_calories", 0)
    menu.total_protein = n.get("total_protein", 0.0)
    menu.total_fat = n.get("total_fat", 0.0)
    menu.total_carbs = n.get("total_carbs", 0.0)
    menu.avg_calories = n.get("avg_calories", 0)
    menu.avg_protein = n.get("avg_protein", 0.0)
    menu.avg_fat = n.get("avg_fat", 0.0)
    menu.avg_carbs = n.get("avg_carbs", 0.0)
    menu.estimated_cost = n.get("total_cost", 0)
    db.commit()
    db.refresh(menu)
    items = build_shopping_from_menu(db, user, menu.meals, user.family_size)
    replace_week_shopping(db, user, menu.week_start, items)
    data = enrich_menu(menu, db, user)
    data["score"] = result["score"]
    return data


@router.get("/current")
def get_current_menu(
    week_start: date | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    menu = get_or_create_week(db, user, week_start)
    return enrich_menu(menu, db, user)


@router.put("/{menu_id}")
def update_menu(menu_id: int, payload: MenuUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    menu = db.query(WeeklyMenu).filter(WeeklyMenu.id == menu_id, WeeklyMenu.user_id == user.id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Меню не найдено")
    meals = sanitize_meals(payload.meals.model_dump())
    menu.meals = meals
    n = calculate_weekly_meals_nutrition(meals, db)
    menu.total_calories = n["total_calories"]
    menu.total_protein = n["total_protein"]
    menu.total_fat = n["total_fat"]
    menu.total_carbs = n["total_carbs"]
    menu.avg_calories = n["avg_calories"]
    menu.avg_protein = n["avg_protein"]
    menu.avg_fat = n["avg_fat"]
    menu.avg_carbs = n["avg_carbs"]
    menu.estimated_cost = n.get("total_cost")
    db.commit()
    items = build_shopping_from_menu(db, user, menu.meals, user.family_size)
    replace_week_shopping(db, user, menu.week_start, items)
    return enrich_menu(menu, db, user)


@router.post("/slot")
def assign_slot(payload: SlotAssign, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    menu = get_or_create_week(db, user)
    meals = sanitize_meals(menu.meals or empty_meals())
    day_key = payload.day.value if hasattr(payload.day, "value") else str(payload.day)
    slot_key = payload.slot.value if hasattr(payload.slot, "value") else str(payload.slot)
    day = meals.setdefault(day_key, {})
    if payload.custom:
        day[slot_key] = payload.custom
    else:
        day[slot_key] = payload.recipe_id
    menu.meals = meals
    n = calculate_weekly_meals_nutrition(meals, db)
    menu.total_calories = n["total_calories"]
    menu.total_protein = n["total_protein"]
    menu.total_fat = n["total_fat"]
    menu.total_carbs = n["total_carbs"]
    menu.avg_calories = n["avg_calories"]
    menu.avg_protein = n["avg_protein"]
    menu.avg_fat = n["avg_fat"]
    menu.avg_carbs = n["avg_carbs"]
    menu.estimated_cost = n.get("total_cost")
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(menu, "meals")
    db.commit()
    items = build_shopping_from_menu(db, user, menu.meals, user.family_size)
    replace_week_shopping(db, user, menu.week_start, items)
    return enrich_menu(menu, db, user)


@router.post("/copy-previous")
def copy_previous(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    current = get_or_create_week(db, user)
    prev = (
        db.query(WeeklyMenu)
        .filter(WeeklyMenu.user_id == user.id, WeeklyMenu.week_start < current.week_start)
        .order_by(WeeklyMenu.week_start.desc())
        .first()
    )
    if not prev:
        raise HTTPException(status_code=404, detail="Прошлой недели ещё нет")
    current.meals = prev.meals
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(current, "meals")
    n = calculate_weekly_meals_nutrition(current.meals, db)
    current.total_calories = n["total_calories"]
    current.total_protein = n["total_protein"]
    current.total_fat = n["total_fat"]
    current.total_carbs = n["total_carbs"]
    current.avg_calories = n["avg_calories"]
    current.avg_protein = n["avg_protein"]
    current.avg_fat = n["avg_fat"]
    current.avg_carbs = n["avg_carbs"]
    db.commit()
    items = build_shopping_from_menu(db, user, current.meals, user.family_size)
    replace_week_shopping(db, user, current.week_start, items)
    return enrich_menu(current, db, user)


@router.get("/history")
def history(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = (
        db.query(WeeklyMenu)
        .filter(WeeklyMenu.user_id == user.id)
        .order_by(WeeklyMenu.week_start.desc())
        .limit(24)
        .all()
    )
    return [
        {
            "id": m.id,
            "week_start": m.week_start,
            "week_end": m.week_end,
            "avg_calories": m.avg_calories,
            "estimated_cost": m.estimated_cost,
            "banned": m.banned,
            "template": m.template,
        }
        for m in rows
    ]


@router.post("/{menu_id}/repeat")
def repeat_menu(menu_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    source = db.query(WeeklyMenu).filter(WeeklyMenu.id == menu_id, WeeklyMenu.user_id == user.id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Неделя не найдена")
    current = get_or_create_week(db, user)
    current.meals = source.meals
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(current, "meals")
    n = calculate_weekly_meals_nutrition(current.meals, db)
    current.total_calories = n["total_calories"]
    current.avg_calories = n["avg_calories"]
    current.total_protein = n["total_protein"]
    current.total_fat = n["total_fat"]
    current.total_carbs = n["total_carbs"]
    db.commit()
    return enrich_menu(current, db, user)


@router.post("/{menu_id}/ban")
def ban_menu(menu_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    menu = db.query(WeeklyMenu).filter(WeeklyMenu.id == menu_id, WeeklyMenu.user_id == user.id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Неделя не найдена")
    menu.banned = True
    ids = []
    for slots in (menu.meals or {}).values():
        if isinstance(slots, dict):
            for v in slots.values():
                if isinstance(v, int):
                    ids.append(v)
                elif isinstance(v, dict) and v.get("recipe_id"):
                    ids.append(v["recipe_id"])
    banned = set(user.banned_recipe_ids or [])
    banned.update(ids)
    user.banned_recipe_ids = list(banned)
    db.commit()
    return {"ok": True, "banned_recipe_ids": user.banned_recipe_ids}


@router.get("/stats")
def stats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(WeeklyMenu).filter(WeeklyMenu.user_id == user.id).all()
    from collections import Counter
    counter = Counter()
    calories = []
    costs = []
    for m in rows:
        calories.append(m.avg_calories or 0)
        costs.append(m.estimated_cost or 0)
        for slots in (m.meals or {}).values():
            if isinstance(slots, dict):
                for v in slots.values():
                    rid = v.get("recipe_id") if isinstance(v, dict) else v
                    if rid:
                        counter[int(rid)] += 1
    top_ids = [i for i, _ in counter.most_common(8)]
    recipes = db.query(Recipe).filter(Recipe.id.in_(top_ids)).all() if top_ids else []
    names = {r.id: r.name for r in recipes}
    return {
        "weeks": len(rows),
        "avg_calories": round(sum(calories) / len(calories), 1) if calories else 0,
        "avg_budget": round(sum(costs) / len(costs), 1) if costs else 0,
        "frequent": [{"id": i, "name": names.get(i, f"#{i}"), "count": c} for i, c in counter.most_common(8)],
        "norm": calculate_user_norm(user),
    }
