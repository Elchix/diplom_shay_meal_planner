# update_russian_nutrition.py
# Обновляет КБЖУ для русских рецептов из локальной базы продуктов

from database import SessionLocal
from models import Recipe
from services.ingredients import normalize_list
from nutrition_base import get_nutrition

def update_russian_recipes(limit=None):
    """Обновляет КБЖУ для русских рецептов из локальной базы"""
    db = SessionLocal()
    
    # Берём русские рецепты с нулевыми калориями (ещё не обновлённые)
    query = db.query(Recipe).filter(
        Recipe.cuisine != '',
        Recipe.calories == 0
    )
    
    if limit:
        query = query.limit(limit)
    
    recipes = query.all()
    
    print(f"Начинаем обновление КБЖУ для {len(recipes)} рецептов...")
    count = 0
    
    for recipe in recipes:
        if recipe.ingredients and len(recipe.ingredients) > 0:
            total = {'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0}
            
            for ingredient in recipe.ingredients:
                item = ingredient if isinstance(ingredient, dict) else {"name": ingredient}
                name = item.get("name") or ""
                nutrition = get_nutrition(name)
                total['calories'] += nutrition['calories'] * 0.5
                total['protein'] += nutrition['protein'] * 0.5
                total['fat'] += nutrition['fat'] * 0.5
                total['carbs'] += nutrition['carbs'] * 0.5
            
            recipe.calories = round(total['calories'])
            recipe.protein = round(total['protein'], 1)
            recipe.fat = round(total['fat'], 1)
            recipe.carbs = round(total['carbs'], 1)
            
            db.commit()
            count += 1
            
            if count % 100 == 0:
                print(f"📊 Обработано {count} рецептов...")
    
    db.close()
    print(f"✅ Обновлено КБЖУ для {count} рецептов!")

if __name__ == "__main__":
    # Запускаем без лимита — все рецепты
    update_russian_recipes()