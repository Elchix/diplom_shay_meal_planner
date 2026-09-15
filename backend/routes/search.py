from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text, or_, func, String
from database import get_db
from models import Recipe
from services.nutrition import serialize_recipe

router = APIRouter(prefix="/api/search", tags=["search"])

_model = None


def get_model():
    global _model
    if _model is False:
        return None
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer("sergeyzh/rubert-tiny-turbo")
        except Exception:
            _model = False
            return None
    return _model


@router.get("/recipes")
def search_recipes(
    q: str = Query(..., description="Поисковый запрос"),
    limit: int = Query(12, ge=1, le=50),
    min_calories: int = Query(None),
    max_calories: int = Query(None),
    semantic: bool = Query(False),
    db: Session = Depends(get_db),
):
    model = get_model() if semantic else None
    if model is not None:
        query_embedding = model.encode(q).tolist()
        sql = """
            SELECT id, 1 - (embedding <=> CAST(:embedding AS vector)) as similarity
            FROM recipes
            WHERE embedding IS NOT NULL
        """
        params = {"embedding": query_embedding}
        if min_calories is not None:
            sql += " AND calories >= :min_calories"
            params["min_calories"] = min_calories
        if max_calories is not None:
            sql += " AND calories <= :max_calories"
            params["max_calories"] = max_calories
        sql += " ORDER BY embedding <=> CAST(:embedding AS vector) LIMIT :limit"
        params["limit"] = limit
        rows = db.execute(text(sql), params).fetchall()
        ids = [r.id for r in rows]
        recipes = {r.id: r for r in db.query(Recipe).filter(Recipe.id.in_(ids)).all()} if ids else {}
        out = []
        for r in rows:
            rec = recipes.get(r.id)
            if rec:
                item = serialize_recipe(rec)
                item["similarity"] = round(r.similarity, 3)
                out.append(item)
        return out

    query = db.query(Recipe).filter(
        or_(
            Recipe.name.ilike(f"%{q}%"),
            func.cast(Recipe.ingredients, String).ilike(f"%{q}%"),
        )
    )
    if min_calories is not None:
        query = query.filter(Recipe.calories >= min_calories)
    if max_calories is not None:
        query = query.filter(Recipe.calories <= max_calories)
    rows = query.order_by(Recipe.popularity.desc().nullslast()).limit(limit).all()
    return [serialize_recipe(r) for r in rows]
