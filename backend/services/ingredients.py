"""Нормализация ингредиентов и классификация рецептов."""

import re
from services.catalog import RECIPE_TAGS, grocery_category_for, estimate_item_cost

MEAT_WORDS = [
    "мясо", "говядин", "свинин", "курица", "куриц", "индейк", "баранин",
    "телятин", "утка", "кролик", "фарш", "бекон", "ветчин", "колбас",
]
FISH_WORDS = ["рыб", "лосос", "семг", "треск", "минтай", "форел", "кревет", "кальмар", "мидии", "тунец"]
ANIMAL_WORDS = MEAT_WORDS + FISH_WORDS + [
    "молок", "сыр", "творог", "яйц", "сливк", "сметан", "кефир", "йогурт",
    "масло сливоч", "ряженк",
]
GLUTEN_WORDS = ["мука пшенич", "пшенич", "хлеб", "макарон", "спагетти", "паста", "манк", "сухар"]
LACTOSE_WORDS = ["молок", "сыр", "творог", "сметан", "сливк", "кефир", "йогурт", "ряженк", "масло сливоч"]

BREAKFAST_HINTS = ["завтрак", "каша", "омлет", "сырник", "блин", "тост", "смузи", "granola", "яичниц"]
LUNCH_HINTS = ["суп", "борщ", "щи", "солянка", "салат", "рассольник", "уха", "харчо"]
DINNER_HINTS = ["основн", "мясо", "рыба", "паста", "запекан", "плов", "гуляш", "котлет", "стейк", "жаркое"]
SNACK_HINTS = ["закуск", "десерт", "выпечк", "напиток", "печень", "кекс", "мусс"]


def _num(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", ".")
    text = text.replace("½", "0.5").replace("¼", "0.25").replace("¾", "0.75")
    match = re.search(r"\d+(\.\d+)?", text)
    return float(match.group()) if match else None


def ingredient_name(item) -> str:
    if item is None:
        return ""
    if isinstance(item, str):
        return item.strip()
    if isinstance(item, dict):
        return str(item.get("name") or item.get("title") or "").strip()
    return str(item).strip()


def normalize_ingredient(item) -> dict:
    if isinstance(item, dict):
        name = ingredient_name(item)
        amount = _num(item.get("amount") if item.get("amount") is not None else item.get("value"))
        unit = item.get("unit") or item.get("type") or ""
        notes = item.get("notes") or ""
        return {
            "name": name,
            "amount": amount,
            "unit": str(unit).strip(),
            "notes": str(notes).strip() if notes else "",
            "category": grocery_category_for(name),
        }
    name = ingredient_name(item)
    return {
        "name": name,
        "amount": None,
        "unit": "",
        "notes": "",
        "category": grocery_category_for(name),
    }


def normalize_list(raw) -> list[dict]:
    if not raw:
        return []
    if isinstance(raw, str):
        return [normalize_ingredient(part.strip()) for part in raw.split(",") if part.strip()]
    return [normalize_ingredient(x) for x in raw if ingredient_name(x)]


def names_of(raw) -> list[str]:
    return [x["name"] for x in normalize_list(raw) if x["name"]]


def contains_any(recipe_ingredients, keywords) -> bool:
    blob = " ".join(names_of(recipe_ingredients)).lower()
    return any(k in blob for k in keywords)


def infer_dish_type(recipe) -> str:
    if getattr(recipe, "dish_type", None):
        return recipe.dish_type
    cat = (recipe.category or "").lower()
    ings = recipe.ingredients
    if contains_any(ings, FISH_WORDS) or "рыб" in cat:
        return "fish"
    if any(w in cat for w in ["десерт", "выпечк", "слад"]):
        return "dessert"
    if contains_any(ings, ["курица", "куриц", "индейк"]) or "птиц" in cat:
        return "poultry"
    if contains_any(ings, MEAT_WORDS) or "мяс" in cat:
        return "meat"
    if "салат" in cat or "овощ" in cat or "вегетар" in cat:
        return "veg"
    return "other"


def infer_meal_slot(recipe) -> str:
    blob = f"{recipe.category or ''} {recipe.name or ''}".lower()
    if any(h in blob for h in BREAKFAST_HINTS):
        return "breakfast"
    if any(h in blob for h in SNACK_HINTS) and not any(h in blob for h in LUNCH_HINTS + DINNER_HINTS):
        return "snack2" if abs(hash(blob)) % 2 else "snack1"
    if any(h in blob for h in LUNCH_HINTS):
        return "lunch"
    if any(h in blob for h in DINNER_HINTS):
        return "dinner"
    if (recipe.calories or 0) < 180:
        return "snack1"
    if (recipe.calories or 0) < 350:
        return "breakfast"
    return "lunch"


def infer_tags(recipe) -> list[str]:
    tags = list(recipe.tags or []) if getattr(recipe, "tags", None) else []
    total = (recipe.total_time or 0) or ((recipe.prep_time or 0) + (recipe.cook_time or 0))
    cal = recipe.calories or 0
    protein = recipe.protein or 0
    ings = recipe.ingredients
    if total and total <= 30 and "до 30 минут" not in tags:
        tags.append("до 30 минут")
    if cal and cal <= 250 and "низкокалорийное" not in tags:
        tags.append("низкокалорийное")
    if protein and protein >= 25 and "высокобелковое" not in tags:
        tags.append("высокобелковое")
    if not contains_any(ings, GLUTEN_WORDS) and "без глютена" not in tags:
        tags.append("без глютена")
    if not contains_any(ings, LACTOSE_WORDS) and "без лактозы" not in tags:
        tags.append("без лактозы")
    cost = getattr(recipe, "estimated_cost", None) or estimate_recipe_cost(recipe)
    if cost and cost <= 180 and "бюджетное" not in tags:
        tags.append("бюджетное")
    if cal and 180 < cal < 450 and "здоровое" not in tags:
        tags.append("здоровое")
    return [t for t in tags if t in RECIPE_TAGS or True]


def estimate_recipe_cost(recipe) -> float:
    if getattr(recipe, "estimated_cost", None):
        return float(recipe.estimated_cost)
    total = 0.0
    for item in normalize_list(recipe.ingredients):
        total += estimate_item_cost(item["name"], item["amount"], item["unit"])
    return round(total or 120.0, 1)


def veg_colors(recipe) -> list[str]:
    blob = " ".join(names_of(recipe.ingredients)).lower()
    colors = []
    mapping = {
        "green": ["огур", "салат", "укроп", "петруш", "шпинат", "брокколи", "кабач", "зелен"],
        "red": ["помидор", "томат", "свекл", "перец крас", "клубник"],
        "orange": ["морков", "тыкв", "апельсин", "сладкий картофель"],
        "yellow": ["перец желт", "кукуруз", "лимон"],
        "white": ["капуст", "лук", "чеснок", "цветн", "картофел"],
        "purple": ["баклажан", "краснокочан", "ягод"],
    }
    for color, keys in mapping.items():
        if any(k in blob for k in keys):
            colors.append(color)
    return colors


def scale_amount(amount, from_serv, to_serv):
    if amount is None:
        return None
    try:
        base = float(from_serv or 1) or 1
        target = float(to_serv or base) or base
        return round(float(amount) * (target / base), 2)
    except (TypeError, ValueError):
        return amount
