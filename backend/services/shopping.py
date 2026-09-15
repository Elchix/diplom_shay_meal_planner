from collections import defaultdict
from models import PantryItem, StapleItem, ShoppingItem, Recipe
from services.ingredients import normalize_list, ingredient_name, scale_amount
from services.catalog import grocery_category_for, cheaper_swap_for, DEFAULT_STAPLES
from services.nutrition import load_recipes_map, _recipe_id_from_slot


def build_shopping_from_menu(db, user, meals: dict, servings_target: int | None = None):
    recipes = load_recipes_map(meals, db)
    merged = defaultdict(lambda: {"amount": 0.0, "unit": "", "names": set(), "notes": []})
    for day_meals in (meals or {}).values():
        if not isinstance(day_meals, dict):
            continue
        for value in day_meals.values():
            rid = _recipe_id_from_slot(value)
            if not rid or rid not in recipes:
                if isinstance(value, dict) and value.get("name") and not rid:
                    key = value["name"].strip().lower()
                    merged[key]["names"].add(value["name"])
                continue
            recipe = recipes[rid]
            target = servings_target or recipe.servings or 2
            for item in normalize_list(recipe.ingredients):
                key = item["name"].lower()
                qty = scale_amount(item["amount"], recipe.servings or 2, target)
                if qty:
                    merged[key]["amount"] += qty
                if item["unit"]:
                    merged[key]["unit"] = item["unit"]
                merged[key]["names"].add(item["name"])
                if item.get("notes"):
                    merged[key]["notes"].append(item["notes"])

    pantry = db.query(PantryItem).filter(PantryItem.user_id == user.id).all()
    pantry_map = {p.name.lower(): p for p in pantry}

    items = []
    for key, data in merged.items():
        name = sorted(data["names"], key=len)[0]
        in_pantry = key in pantry_map
        amount = round(data["amount"], 2) if data["amount"] else None
        if in_pantry and pantry_map[key].amount and amount:
            amount = max(0, amount - float(pantry_map[key].amount))
            if amount == 0:
                continue
        items.append({
            "name": name,
            "amount": amount,
            "unit": data["unit"],
            "category": grocery_category_for(name),
            "note": "; ".join(dict.fromkeys(data["notes"]))[:180] if data["notes"] else None,
            "checked": False,
            "from_menu": True,
            "in_pantry": in_pantry and amount is None,
            "cheaper_swap": cheaper_swap_for(name),
        })

    settings = user.settings or {}
    if settings.get("auto_staples", True):
        staples = db.query(StapleItem).filter(StapleItem.user_id == user.id, StapleItem.enabled.is_(True)).all()
        source = staples or [type("S", (), s) for s in DEFAULT_STAPLES]
        have = {i["name"].lower() for i in items}
        for s in source:
            if s.name.lower() in have:
                continue
            items.append({
                "name": s.name,
                "amount": s.amount,
                "unit": s.unit,
                "category": getattr(s, "category", None) or grocery_category_for(s.name),
                "note": "частая покупка",
                "checked": False,
                "from_menu": False,
                "in_pantry": False,
                "cheaper_swap": None,
            })

    items.sort(key=lambda x: (x["category"], x["name"]))
    return items


def replace_week_shopping(db, user, week_start, items: list[dict]):
    db.query(ShoppingItem).filter(
        ShoppingItem.user_id == user.id,
        ShoppingItem.week_start == week_start,
        ShoppingItem.from_menu.is_(True),
    ).delete(synchronize_session=False)
    saved = []
    for row in items:
        rec = ShoppingItem(
            user_id=user.id,
            week_start=week_start,
            name=row["name"],
            amount=row.get("amount"),
            unit=row.get("unit"),
            category=row.get("category") or "other",
            note=row.get("note"),
            checked=bool(row.get("checked")),
            from_menu=bool(row.get("from_menu", True)),
            in_pantry=bool(row.get("in_pantry")),
            cheaper_swap=row.get("cheaper_swap"),
        )
        db.add(rec)
        saved.append(rec)
    db.commit()
    return saved


def serialize_item(item: ShoppingItem) -> dict:
    return {
        "id": item.id,
        "name": item.name,
        "amount": item.amount,
        "unit": item.unit,
        "category": item.category,
        "note": item.note,
        "checked": item.checked,
        "from_menu": item.from_menu,
        "in_pantry": item.in_pantry,
        "cheaper_swap": item.cheaper_swap,
    }
