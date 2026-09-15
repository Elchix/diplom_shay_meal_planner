from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, String
from database import get_db
from models import Recipe, RecipeCollection, User, PantryItem
from schemas import RecipeCreate, CollectionIn, ImportLinkIn
from auth import get_current_user, optional_user
from services.nutrition import serialize_recipe
from services.ingredients import names_of, infer_tags, infer_dish_type, infer_meal_slot, contains_any
from services.catalog import RECIPE_CATEGORIES, RECIPE_TAGS, grocery_category_for
from services.slots import MealSlot, normalize_slot
from nutrition_base import get_nutrition

router = APIRouter(prefix="/api/recipes", tags=["recipes"])

_semantic_model = None


def _model():
    global _semantic_model
    if _semantic_model is False:
        return None
    if _semantic_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _semantic_model = SentenceTransformer("sergeyzh/rubert-tiny-turbo")
        except Exception:
            _semantic_model = False
            return None
    return _semantic_model


def apply_filters(q, category, complexity, cuisine, tag, max_time, min_cal, max_cal, dish_type, time_bucket, cal_bucket):
    if category:
        q = q.filter(Recipe.category.ilike(f"%{category}%"))
    if complexity:
        q = q.filter(Recipe.complexity.ilike(f"%{complexity}%"))
    if cuisine:
        q = q.filter(Recipe.cuisine.ilike(f"%{cuisine}%"))
    if dish_type:
        q = q.filter(Recipe.dish_type == dish_type)
    if tag:
        q = q.filter(Recipe.tags.contains([tag]))
    if max_time:
        q = q.filter(or_(Recipe.total_time <= max_time, Recipe.cook_time <= max_time))
    if min_cal is not None:
        q = q.filter(Recipe.calories >= min_cal)
    if max_cal is not None:
        q = q.filter(Recipe.calories <= max_cal)
    if time_bucket == "20":
        q = q.filter(or_(Recipe.total_time <= 20, Recipe.cook_time <= 20))
    elif time_bucket == "20-40":
        q = q.filter(or_(Recipe.total_time.between(20, 40), Recipe.cook_time.between(20, 40)))
    elif time_bucket == "40":
        q = q.filter(or_(Recipe.total_time >= 40, Recipe.cook_time >= 40))
    if cal_bucket == "low":
        q = q.filter(Recipe.calories <= 250)
    elif cal_bucket == "mid":
        q = q.filter(Recipe.calories.between(250, 500))
    elif cal_bucket == "high":
        q = q.filter(Recipe.calories >= 500)
    return q


@router.get("")
def list_recipes(
    q: str | None = None,
    ingredient: str | None = None,
    ingredients: str | None = None,
    category: str | None = None,
    complexity: str | None = None,
    cuisine: str | None = None,
    tag: str | None = None,
    dish_type: str | None = None,
    time_bucket: str | None = None,
    cal_bucket: str | None = None,
    max_time: int | None = None,
    sort: str = "popularity",
    pantry: bool = False,
    page: int = 1,
    limit: int = 24,
    db: Session = Depends(get_db),
    user: User | None = Depends(optional_user),
):
    query = db.query(Recipe)
    query = apply_filters(query, category, complexity, cuisine, tag, max_time, None, None, dish_type, time_bucket, cal_bucket)
    if q:
        query = query.filter(or_(Recipe.name.ilike(f"%{q}%"), Recipe.description.ilike(f"%{q}%")))
    must = []
    if ingredient:
        must.append(ingredient)
    if ingredients:
        must += [x.strip() for x in ingredients.split(",") if x.strip()]
    for term in must:
        query = query.filter(func.cast(Recipe.ingredients, String).ilike(f"%{term}%"))

    if pantry and user:
        items = db.query(PantryItem).filter(PantryItem.user_id == user.id).all()
        names = [p.name for p in items if p.name]
        if names:
            cond = [func.cast(Recipe.ingredients, String).ilike(f"%{n}%") for n in names[:12]]
            query = query.filter(or_(*cond))

    if sort == "time":
        query = query.order_by(Recipe.total_time.asc().nullslast(), Recipe.cook_time.asc().nullslast())
    elif sort == "calories":
        query = query.order_by(Recipe.calories.asc().nullslast())
    elif sort == "rating":
        query = query.order_by(Recipe.avg_rating.desc().nullslast())
    elif sort == "new":
        query = query.order_by(Recipe.id.desc())
    else:
        query = query.order_by(Recipe.popularity.desc().nullslast(), Recipe.id.desc())

    total = query.count()
    rows = query.offset((page - 1) * limit).limit(limit).all()
    return {
        "total": total,
        "page": page,
        "items": [serialize_recipe(r) for r in rows],
    }


@router.get("/random")
def random_recipe(
    slot: MealSlot | None = Query(None, description="breakfast | lunch | dinner | snack1 | snack2"),
    db: Session = Depends(get_db),
):
    q = db.query(Recipe).order_by(func.random())
    slot_key = normalize_slot(slot.value if slot else None)
    if slot_key == "breakfast":
        q = q.filter(or_(Recipe.category.ilike("%завтрак%"), Recipe.name.ilike("%каша%"), Recipe.name.ilike("%омлет%")))
    elif slot_key == "lunch":
        q = q.filter(or_(Recipe.category.ilike("%суп%"), Recipe.category.ilike("%салат%")))
    elif slot_key == "dinner":
        q = q.filter(or_(Recipe.category.ilike("%мяс%"), Recipe.category.ilike("%рыб%"), Recipe.category.ilike("%основ%")))
    elif slot_key in ("snack1", "snack2"):
        q = q.filter(or_(Recipe.category.ilike("%закуск%"), Recipe.category.ilike("%десерт%"), Recipe.name.ilike("%тост%")))
    recipe = q.first()
    if not recipe:
        recipe = db.query(Recipe).order_by(func.random()).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Рецептов пока нет")
    return serialize_recipe(recipe)


@router.get("/collections/mine")
def my_collections(list_name: str | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = db.query(RecipeCollection).filter(RecipeCollection.user_id == user.id)
    if list_name:
        q = q.filter(RecipeCollection.list_name == list_name)
    rows = q.all()
    ids = [r.recipe_id for r in rows]
    recipes = {r.id: r for r in db.query(Recipe).filter(Recipe.id.in_(ids)).all()} if ids else {}
    grouped = {}
    for row in rows:
        grouped.setdefault(row.list_name, [])
        rec = recipes.get(row.recipe_id)
        if rec:
            grouped[row.list_name].append(serialize_recipe(rec))
    return grouped


@router.get("/{recipe_id}")
def get_recipe(recipe_id: int, servings: int | None = None, db: Session = Depends(get_db)):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Рецепт не найден")
    recipe.popularity = (recipe.popularity or 0) + 1
    db.commit()
    return serialize_recipe(recipe, servings)


@router.post("")
def create_recipe(payload: RecipeCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ings = payload.ingredients
    calories = payload.calories
    protein = payload.protein
    fat = payload.fat
    carbs = payload.carbs
    if calories is None:
        total = {"calories": 0, "protein": 0, "fat": 0, "carbs": 0}
        for item in ings:
            name = item.get("name") if isinstance(item, dict) else str(item)
            n = get_nutrition(name)
            qty = 0.6
            for k in total:
                total[k] += n[k] * qty
        calories, protein, fat, carbs = total["calories"], total["protein"], total["fat"], total["carbs"]
    recipe = Recipe(
        name=payload.name,
        description=payload.description,
        ingredients=ings,
        steps=payload.steps,
        category=payload.category,
        cuisine=payload.cuisine,
        complexity=payload.complexity,
        image_url=payload.image_url,
        tags=payload.tags,
        substitutions=payload.substitutions,
        video_url=payload.video_url,
        prep_time=payload.prep_time or 0,
        cook_time=payload.cook_time or 0,
        total_time=(payload.prep_time or 0) + (payload.cook_time or 0),
        servings=payload.servings or 2,
        calories=round(calories or 0),
        protein=round(protein or 0, 1),
        fat=round(fat or 0, 1),
        carbs=round(carbs or 0, 1),
        dish_type=payload.dish_type,
        estimated_cost=payload.estimated_cost,
        url=payload.url,
        is_user_recipe=True,
        owner_id=user.id,
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return serialize_recipe(recipe)


@router.post("/import-link")
def import_link(payload: ImportLinkIn, user: User = Depends(get_current_user)):
    url = payload.url.strip()
    host = url.split("/")[2] if "://" in url else "рецепт"
    name = host.replace("www.", "").split(".")[0].capitalize() + " — блюдо по ссылке"
    return {
        "name": name,
        "description": f"Черновик по ссылке {url}. Проверьте ингредиенты и шаги.",
        "url": url,
        "video_url": url if "youtu" in url else None,
        "category": "основные",
        "cuisine": "другая",
        "complexity": "средне",
        "prep_time": 15,
        "cook_time": 25,
        "servings": 2,
        "ingredients": [
            {"name": "основной продукт", "amount": 400, "unit": "г"},
            {"name": "лук репчатый", "amount": 1, "unit": "шт"},
            {"name": "масло растительное", "amount": 2, "unit": "ст.л."},
            {"name": "соль", "amount": 1, "unit": "ч.л."},
        ],
        "steps": [
            {"text": "Подготовить продукты из ссылки и скорректировать количества."},
            {"text": "Обжарить основу, добавить специи."},
            {"text": "Довести до готовности и подавать."},
        ],
        "tags": ["до 30 минут"],
    }


@router.post("/collections")
def add_collection(payload: CollectionIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    exists = (
        db.query(RecipeCollection)
        .filter(
            RecipeCollection.user_id == user.id,
            RecipeCollection.recipe_id == payload.recipe_id,
            RecipeCollection.list_name == payload.list_name,
        )
        .first()
    )
    if exists:
        return {"ok": True, "id": exists.id}
    row = RecipeCollection(user_id=user.id, recipe_id=payload.recipe_id, list_name=payload.list_name)
    db.add(row)
    db.commit()
    return {"ok": True, "id": row.id}


@router.delete("/collections")
def remove_collection(recipe_id: int, list_name: str = "favorites", db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    db.query(RecipeCollection).filter(
        RecipeCollection.user_id == user.id,
        RecipeCollection.recipe_id == recipe_id,
        RecipeCollection.list_name == list_name,
    ).delete()
    db.commit()
    return {"ok": True}
