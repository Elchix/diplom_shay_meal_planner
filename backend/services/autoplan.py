import random
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from models import Recipe, User, FamilyMember
from services.nutrition import calculate_user_norm, calculate_weekly_meals_nutrition
from services.ingredients import (
    contains_any, infer_meal_slot, infer_tags, names_of, estimate_recipe_cost, veg_colors,
)
from services.slots import VALID_SLOTS, normalize_slot, normalize_slot_list, clean_text, clean_str_list
from services.catalog import TEMPLATES

DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
DEFAULT_SLOTS = list(VALID_SLOTS)


class AutoPlanGenerator:
    def __init__(self, db: Session, user: User, preferences: dict | None = None):
        self.db = db
        self.user = user
        self.pref = preferences or {}
        template_key = clean_text(self.pref.get("template"))
        self.template = TEMPLATES.get(template_key or "", {})
        settings = user.settings or {}
        raw_slots = self.pref.get("meal_slots") or settings.get("meal_slots") or DEFAULT_SLOTS
        self.slots = normalize_slot_list(raw_slots) or list(DEFAULT_SLOTS)
        if self.pref.get("quick_only"):
            self.max_time = 30
        else:
            self.max_time = self.pref.get("max_time") or self.template.get("max_time") or settings.get("cooking_time_limit")
        self.diet = clean_text(self.pref.get("diet_type") or self.template.get("diet") or user.diet_type) or ""
        self.disliked = [x.lower() for x in clean_str_list(self.pref.get("disliked") or user.disliked_ingredients or [])]
        self.allergies = [x.lower() for x in clean_str_list(user.allergies or [])]
        members = db.query(FamilyMember).filter(FamilyMember.user_id == user.id).all()
        for m in members:
            self.allergies += [x.lower() for x in (m.allergies or [])]
            self.disliked += [x.lower() for x in (m.dislikes or [])]
        self.banned = set(user.banned_recipe_ids or [])
        self.favorites = set(self.pref.get("favorites") or user.favorite_recipe_ids or [])
        self.budget = self.pref.get("budget") or user.budget
        self.pool = self._load_pool()
        self.by_slot = {s: [] for s in self.slots}
        for recipe in self.pool:
            slot = infer_meal_slot(recipe)
            mapped = normalize_slot(slot) or slot
            if mapped in self.by_slot:
                self.by_slot[mapped].append(recipe)
            if mapped == "snack1" and "snack2" in self.by_slot:
                self.by_slot["snack2"].append(recipe)
            if mapped == "lunch" and "dinner" in self.by_slot and len(self.by_slot["dinner"]) < 80:
                self.by_slot["dinner"].append(recipe)
        for slot, rows in self.by_slot.items():
            if len(rows) < 8:
                self.by_slot[slot] = list(self.pool)

    def _load_pool(self):
        q = self.db.query(Recipe).filter(
            Recipe.name.isnot(None),
            Recipe.steps.isnot(None)
        )
        if self.banned:
            q = q.filter(~Recipe.id.in_(list(self.banned)[:200]))
        if self.max_time:
            q = q.filter(
                or_(
                    Recipe.total_time <= self.max_time,
                    Recipe.cook_time <= self.max_time,
                    Recipe.total_time.is_(None),
                )
            )
        diet = self.diet.lower()
        if diet in ("vegetarian", "вегетарианское"):
            q = q.filter(~Recipe.name.ilike("%мяс%"))
        rows = q.order_by(func.random()).limit(700).all()
        filtered = [r for r in rows if self._recipe_ok(r)]
        return filtered or rows[:200]

    def _recipe_ok(self, recipe: Recipe) -> bool:
        blob = " ".join(names_of(recipe.ingredients) + [recipe.name or ""]).lower()
        if any(a and a in blob for a in self.allergies):
            return False
        if any(d and d in blob for d in self.disliked):
            return False
        diet = self.diet.lower()
        if diet in ("vegetarian", "вегетарианское") and contains_any(recipe.ingredients, ["говядин", "свинин", "курица", "куриц", "рыб", "фарш"]):
            return False
        if diet in ("vegan", "веганское") and contains_any(recipe.ingredients, ["говядин", "свинин", "курица", "молок", "сыр", "яйц", "сметан"]):
            return False
        return True

    def generate(self, iterations: int = 250) -> dict:
        best_score = -1e9
        best_menu = None
        best_nutrition = None
        if not self.pool:
            raise ValueError("Нет подходящих рецептов для автоплана")
        n = max(40, min(iterations, 400))
        for _ in range(n):
            menu = self._random_menu()
            nutrition = calculate_weekly_meals_nutrition(menu, self.db, {r.id: r for r in self.pool})
            score = self._score(menu, nutrition)
            if score > best_score:
                best_score = score
                best_menu = menu
                best_nutrition = nutrition
        if best_menu is None:
            best_menu = self._random_menu()
            best_nutrition = calculate_weekly_meals_nutrition(best_menu, self.db, {r.id: r for r in self.pool})
            best_score = 0
        return {"menu": best_menu, "nutrition": best_nutrition, "score": round(best_score, 2)}

    def _random_menu(self) -> dict:
        used = set()
        menu = {}
        for day in DAYS:
            menu[day] = {}
            for slot in self.slots:
                candidates = [r for r in self.by_slot.get(slot, self.pool) if r.id not in used]
                if len(candidates) < 4:
                    candidates = self.by_slot.get(slot) or self.pool
                if self.favorites and random.random() < 0.22:
                    favs = [r for r in candidates if r.id in self.favorites]
                    if favs:
                        candidates = favs
                tags_pref = self.template.get("prefer_tags") or []
                if tags_pref and random.random() < 0.35:
                    tagged = [r for r in candidates if any(t in infer_tags(r) for t in tags_pref)]
                    if tagged:
                        candidates = tagged
                recipe = random.choice(candidates)
                used.add(recipe.id)
                menu[day][slot] = recipe.id
        return menu

    def _score(self, menu: dict, nutrition: dict) -> float:
        norm = calculate_user_norm(self.user)
        score = 0.0
        if norm["calories"]:
            diff = abs(nutrition["avg_calories"] - norm["calories"]) / norm["calories"]
            score += max(0, 40 - diff * 80)
        score += max(0, 20 - abs(nutrition["avg_protein"] / max(norm["protein"], 1) - 1) * 20)
        unique = nutrition.get("unique_dishes") or 0
        total_slots = sum(len(v) for v in menu.values())
        score += (unique / max(total_slots, 1)) * 20
        score += max(0, 15 - nutrition.get("repeats", 0) * 5)
        colors = nutrition.get("colors") or []
        score += min(10, len(colors) * 2)
        if self.budget and nutrition.get("total_cost"):
            if nutrition["total_cost"] <= self.budget:
                score += 10
            else:
                score -= min(20, (nutrition["total_cost"] - self.budget) / max(self.budget, 1) * 20)
        if self.max_time:
            overtime = 0
            idmap = {r.id: r for r in self.pool}
            for day in menu.values():
                for rid in day.values():
                    rec = idmap.get(rid)
                    t = (rec.total_time or rec.cook_time or 0) if rec else 0
                    if t > self.max_time:
                        overtime += 1
            score -= overtime * 2
        return score
