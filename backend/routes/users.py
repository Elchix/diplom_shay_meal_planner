from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, FamilyMember
from schemas import UserCreate, UserResponse, LoginRequest, UserUpdate, FamilyMemberIn
from auth import get_password_hash, create_access_token, verify_password, get_current_user
from services.nutrition import calculate_user_norm
from services.slots import normalize_slot_list, VALID_SLOTS

router = APIRouter(prefix="/api/users", tags=["users"])


def _safe_settings(settings):
    data = dict(settings or {})
    data.setdefault("week_starts_on", "monday")
    data.setdefault("units", "metric")
    data.setdefault("theme", "light")
    data.setdefault("reminders", True)
    data.setdefault("auto_staples", True)
    data["meal_slots"] = normalize_slot_list(data.get("meal_slots")) or list(VALID_SLOTS)
    return data


def dump_user(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "age": user.age,
        "weight": user.weight,
        "height": user.height,
        "sex": user.sex,
        "activity": user.activity,
        "goal": user.goal,
        "diet_type": user.diet_type,
        "allergies": user.allergies or [],
        "disliked_ingredients": user.disliked_ingredients or [],
        "favorite_recipe_ids": user.favorite_recipe_ids or [],
        "banned_recipe_ids": user.banned_recipe_ids or [],
        "budget": user.budget,
        "family_size": user.family_size or 1,
        "settings": _safe_settings(user.settings),
        "norm": calculate_user_norm(user),
    }


@router.post("/register")
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    new_user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        name=user_data.name,
        age=user_data.age,
        weight=user_data.weight,
        height=user_data.height,
        sex=user_data.sex,
        activity=user_data.activity,
        goal=user_data.goal,
        diet_type=user_data.diet_type,
        allergies=user_data.allergies,
        disliked_ingredients=user_data.disliked_ingredients,
        budget=user_data.budget,
        family_size=user_data.family_size or 1,
        settings={
            "meal_slots": ["breakfast", "lunch", "dinner", "snack1", "snack2"],
            "week_starts_on": "monday",
            "units": "metric",
            "theme": "light",
            "reminders": True,
            "auto_staples": True,
        },
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    token = create_access_token({"sub": str(new_user.id)})
    return {"access_token": token, "token_type": "bearer", "user": dump_user(new_user)}


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer", "user": dump_user(user)}


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return dump_user(user)


@router.put("/me")
def update_me(payload: UserUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return dump_user(user)


@router.put("/profile/{user_id}")
def update_profile(user_id: int, payload: UserUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.id != user_id:
        raise HTTPException(status_code=403, detail="Нельзя менять чужой профиль")
    return update_me(payload, db, user)


@router.get("/family")
def family(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(FamilyMember).filter(FamilyMember.user_id == user.id).all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "role": r.role,
            "allergies": r.allergies or [],
            "dislikes": r.dislikes or [],
            "favorites": r.favorites or [],
            "portions": r.portions,
        }
        for r in rows
    ]


@router.post("/family")
def add_family(payload: FamilyMemberIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = FamilyMember(
        user_id=user.id,
        name=payload.name,
        role=payload.role,
        allergies=payload.allergies,
        dislikes=payload.dislikes,
        favorites=payload.favorites,
        portions=payload.portions if payload.role != "child" else (payload.portions or 0.6),
    )
    db.add(row)
    members = db.query(FamilyMember).filter(FamilyMember.user_id == user.id).count() + 1
    user.family_size = max(1, members)
    db.commit()
    db.refresh(row)
    return {"id": row.id, **payload.model_dump()}


@router.delete("/family/{member_id}")
def delete_family(member_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = db.query(FamilyMember).filter(FamilyMember.id == member_id, FamilyMember.user_id == user.id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Член семьи не найден")
    db.delete(row)
    db.commit()
    return {"ok": True}
