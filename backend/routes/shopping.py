from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, ShoppingItem
from schemas import ShoppingPatch, ShoppingAdd
from auth import get_current_user
from routes.menu import get_or_create_week
from services.shopping import build_shopping_from_menu, replace_week_shopping, serialize_item
from services.catalog import GROCERY_CATEGORIES, grocery_category_for

router = APIRouter(prefix="/api/shopping", tags=["shopping"])


@router.get("")
def list_shopping(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    menu = get_or_create_week(db, user)
    rows = (
        db.query(ShoppingItem)
        .filter(ShoppingItem.user_id == user.id, ShoppingItem.week_start == menu.week_start)
        .all()
    )
    if not rows:
        built = build_shopping_from_menu(db, user, menu.meals, user.family_size)
        rows = replace_week_shopping(db, user, menu.week_start, built)
        db.commit()
        rows = (
            db.query(ShoppingItem)
            .filter(ShoppingItem.user_id == user.id, ShoppingItem.week_start == menu.week_start)
            .all()
        )
    grouped = {c["id"]: [] for c in GROCERY_CATEGORIES}
    for row in rows:
        grouped.setdefault(row.category or "other", []).append(serialize_item(row))
    return {
        "week_start": menu.week_start,
        "categories": GROCERY_CATEGORIES,
        "items": [serialize_item(r) for r in rows],
        "grouped": grouped,
        "done": sum(1 for r in rows if r.checked),
        "total": len(rows),
    }


@router.post("/rebuild")
def rebuild(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    menu = get_or_create_week(db, user)
    built = build_shopping_from_menu(db, user, menu.meals, user.family_size)
    replace_week_shopping(db, user, menu.week_start, built)
    return list_shopping(db, user)


@router.post("/items")
def add_item(payload: ShoppingAdd, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    menu = get_or_create_week(db, user)
    row = ShoppingItem(
        user_id=user.id,
        week_start=menu.week_start,
        name=payload.name,
        amount=payload.amount,
        unit=payload.unit,
        note=payload.note,
        category=payload.category or grocery_category_for(payload.name),
        from_menu=False,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return serialize_item(row)


@router.patch("/items/{item_id}")
def patch_item(item_id: int, payload: ShoppingPatch, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = db.query(ShoppingItem).filter(ShoppingItem.id == item_id, ShoppingItem.user_id == user.id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Позиция не найдена")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    db.commit()
    return serialize_item(row)


@router.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = db.query(ShoppingItem).filter(ShoppingItem.id == item_id, ShoppingItem.user_id == user.id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Позиция не найдена")
    db.delete(row)
    db.commit()
    return {"ok": True}


@router.get("/export.txt")
def export_txt(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    data = list_shopping(db, user)
    lines = ["Список покупок", ""]
    for cat in data["categories"]:
        items = data["grouped"].get(cat["id"]) or []
        if not items:
            continue
        lines.append(cat["label"].upper())
        for it in items:
            mark = "[x]" if it["checked"] else "[ ]"
            qty = f"{it['amount'] or ''} {it['unit'] or ''}".strip()
            note = f" — {it['note']}" if it["note"] else ""
            lines.append(f"{mark} {it['name']} {qty}{note}")
        lines.append("")
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse("\n".join(lines), media_type="text/plain; charset=utf-8")
