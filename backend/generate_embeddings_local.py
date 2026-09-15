import time
from sqlalchemy import text
from database import SessionLocal
from models import Recipe
from sentence_transformers import SentenceTransformer

# Загружаем модель для русского языка
print("Загружаем модель...")
model = SentenceTransformer('sergeyzh/rubert-tiny-turbo')
print("✅ Модель загружена!")

def generate_all_embeddings(limit=None):
    """Генерирует векторы для рецептов с помощью локальной модели"""
    db = SessionLocal()
    
    # Берём рецепты без векторов
    query = db.query(Recipe).filter(Recipe.embedding.is_(None))
    if limit:
        query = query.limit(limit)
    
    recipes = query.all()
    
    print(f"Начинаем генерацию векторов для {len(recipes)} рецептов...")
    count = 0
    
    for recipe in recipes:
        # Формируем текст для векторизации
        from services.ingredients import names_of
        ingredients_text = ", ".join(names_of(recipe.ingredients))
        # ИСПРАВЛЕНО: переменная называется recipe_text, а не text
        recipe_text = f"{recipe.name}. Ингредиенты: {ingredients_text}"
        
        # Генерируем вектор (локально, бесплатно!)
        embedding = model.encode(recipe_text)
        
        # Сохраняем вектор в базу
        db.execute(
            text("UPDATE recipes SET embedding = :embedding WHERE id = :id"),
            {"embedding": embedding.tolist(), "id": recipe.id}
        )
        db.commit()
        count += 1
        
        if count % 100 == 0:
            print(f"Обработано {count}/{len(recipes)} рецептов")
    
    db.close()
    print(f"✅ Сгенерировано векторов для {count} рецептов!")

if __name__ == "__main__":
    # Сначала 10 рецептов для теста
    generate_all_embeddings()
    
    # Когда тест пройдёт успешно, запусти без лимита:
    # generate_all_embeddings()