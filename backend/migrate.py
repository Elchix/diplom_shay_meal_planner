"""Добавляет новые колонки и таблицы без удаления данных."""
from sqlalchemy import text
from database import engine, SessionLocal
from models import Base

ALTERS = [
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS name VARCHAR",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS sex VARCHAR",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS activity VARCHAR",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS disliked_ingredients JSON",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS favorite_recipe_ids JSON",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS banned_recipe_ids JSON",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS family_size INTEGER DEFAULT 1",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS settings JSON",
    "ALTER TABLE recipes ADD COLUMN IF NOT EXISTS tags JSON",
    "ALTER TABLE recipes ADD COLUMN IF NOT EXISTS substitutions JSON",
    "ALTER TABLE recipes ADD COLUMN IF NOT EXISTS video_url VARCHAR",
    "ALTER TABLE recipes ADD COLUMN IF NOT EXISTS estimated_cost FLOAT",
    "ALTER TABLE recipes ADD COLUMN IF NOT EXISTS dish_type VARCHAR",
    "ALTER TABLE recipes ADD COLUMN IF NOT EXISTS is_user_recipe BOOLEAN DEFAULT FALSE",
    "ALTER TABLE recipes ADD COLUMN IF NOT EXISTS owner_id INTEGER",
    "ALTER TABLE recipes ADD COLUMN IF NOT EXISTS popularity INTEGER DEFAULT 0",
    "ALTER TABLE weekly_menus ADD COLUMN IF NOT EXISTS estimated_cost FLOAT DEFAULT 0",
    "ALTER TABLE weekly_menus ADD COLUMN IF NOT EXISTS template VARCHAR",
    "ALTER TABLE weekly_menus ADD COLUMN IF NOT EXISTS banned BOOLEAN DEFAULT FALSE",
]


def migrate():
    print("Обновляем схему...")
    with engine.begin() as conn:
        for sql in ALTERS:
            conn.execute(text(sql))
    Base.metadata.create_all(bind=engine)
    print("Схема готова.")


if __name__ == "__main__":
    migrate()
