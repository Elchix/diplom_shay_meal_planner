from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, PantryItem, Recipe, StapleItem
from schemas import PantryIn
from auth import get_current_user
from services.nutrition import serialize_recipe
from sqlalchemy import func, String, or_

router = APIRouter(prefix="/api/pantry", tags=["pantry"])


def serialize_pantry(item: PantryItem) -> dict:
    days_left = None
    status = "ok"
    if item.expires_on:
        days_left = (item.expires_on - date.today()).days
        if days_left < 0:
            status = "expired"
        elif days_left <= 2:
            status = "expiring"
        elif days_left <= 5:
            status = "use_soon"
    if item.amount is not None and item.amount <= 0.2:
        status = "low"
    return {
        "id": item.id,
        "name": item.name,
        "amount": item.amount,
        "unit": item.unit,
        "location": item.location,
        "expires_on": item.expires_on.isoformat() if item.expires_on else None,
        "days_left": days_left,
        "status": status,
    }


@router.get("")
def list_pantry(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(PantryItem).filter(PantryItem.user_id == user.id).order_by(PantryItem.name).all()
    items = [serialize_pantry(r) for r in rows]
    alerts = [i for i in items if i["status"] in ("expired", "expiring", "use_soon", "low")]
    return {"items": items, "alerts": alerts}


@router.post("")
def add_pantry(payload: PantryIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = PantryItem(
        user_id=user.id,
        name=payload.name,
        amount=payload.amount,
        unit=payload.unit,
        location=payload.location,
        expires_on=payload.expires_on,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return serialize_pantry(row)


@router.put("/{item_id}")
def update_pantry(item_id: int, payload: PantryIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = db.query(PantryItem).filter(PantryItem.id == item_id, PantryItem.user_id == user.id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Продукт не найден")
    row.name = payload.name
    row.amount = payload.amount
    row.unit = payload.unit
    row.location = payload.location
    row.expires_on = payload.expires_on
    db.commit()
    return serialize_pantry(row)


@router.delete("/{item_id}")
def delete_pantry(item_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = db.query(PantryItem).filter(PantryItem.id == item_id, PantryItem.user_id == user.id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Продукт не найден")
    db.delete(row)
    db.commit()
    return {"ok": True}


@router.get("/cook-from")
def cook_from_pantry(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    items = db.query(PantryItem).filter(PantryItem.user_id == user.id).all()
    names = [p.name for p in items if p.name]
    if not names:
        return {"items": [], "hint": "Добавьте продукты в кладовку"}
    cond = [func.cast(Recipe.ingredients, String).ilike(f"%{n}%") for n in names[:10]]
    rows = db.query(Recipe).filter(or_(*cond)).order_by(func.random()).limit(18).all()
    return {"items": [serialize_recipe(r) for r in rows]}


@router.get("/staples")
def staples(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(StapleItem).filter(StapleItem.user_id == user.id).all()
    return [
        {"id": r.id, "name": r.name, "amount": r.amount, "unit": r.unit, "category": r.category, "enabled": r.enabled}
        for r in rows
    ]


@router.post("/staples")
def add_staple(payload: PantryIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = StapleItem(user_id=user.id, name=payload.name, amount=payload.amount, unit=payload.unit)
    db.add(row)
    db.commit()
    return {"id": row.id, "name": row.name}
