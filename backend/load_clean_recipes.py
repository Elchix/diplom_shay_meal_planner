import pandas as pd
import json
import ast
from datetime import datetime
from database import SessionLocal
from models import Recipe

def parse_ingredients(ing_str):
    """Парсит строку ингредиентов в список"""
    if pd.isna(ing_str) or ing_str == '':
        return []
    
    # Если строка выглядит как JSON-массив
    if ing_str.startswith('[') and ing_str.endswith(']'):
        try:
            return json.loads(ing_str)
        except:
            pass
    
    # Если это строка с разделителями (например, "ингр1, ингр2, ингр3")
    if ',' in ing_str:
        return [i.strip() for i in ing_str.split(',') if i.strip()]
    
    # Если это одна строка
    return [ing_str.strip()]

def load_recipes(csv_path="allrecipes.csv"):
    db = SessionLocal()
    db.rollback()
    
    print(f"Читаем файл {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"Всего рецептов: {len(df)}")
    print("Колонки в CSV:", list(df.columns))
    
    print(f"Загружаем рецепты...")
    count = 0
    
    for _, row in df.iterrows():
        try:
            # Парсим ингредиенты
            ingredients_str = row.get('ingredients', '')
            ingredients_list = parse_ingredients(ingredients_str)
            
            # Парсим дату
            date_str = row.get('date_published', '')
            date_published = None
            if pd.notna(date_str) and date_str:
                try:
                    date_published = pd.to_datetime(date_str)
                except:
                    pass
            
            recipe = Recipe(
                name=str(row.get('name', ''))[:255] if pd.notna(row.get('name')) else None,
                url=str(row.get('url', '')) if pd.notna(row.get('url')) else None,
                author=str(row.get('author', '')) if pd.notna(row.get('author')) else None,
                date_published=date_published,
                ingredients=ingredients_list,
                calories=float(row.get('calories', 0)) if pd.notna(row.get('calories')) else None,
                fat=float(row.get('fat', 0)) if pd.notna(row.get('fat')) else None,
                carbs=float(row.get('carbs', 0)) if pd.notna(row.get('carbs')) else None,
                protein=float(row.get('protein', 0)) if pd.notna(row.get('protein')) else None,
                avg_rating=float(row.get('avg_rating', 0)) if pd.notna(row.get('avg_rating')) else None,
                total_ratings=int(row.get('total_ratings', 0)) if pd.notna(row.get('total_ratings')) else None,
                reviews=int(row.get('reviews', 0)) if pd.notna(row.get('reviews')) else None,
                prep_time=int(row.get('prep_time', 0)) if pd.notna(row.get('prep_time')) else None,
                cook_time=int(row.get('cook_time', 0)) if pd.notna(row.get('cook_time')) else None,
                total_time=int(row.get('total_time', 0)) if pd.notna(row.get('total_time')) else None,
                servings=int(row.get('servings', 0)) if pd.notna(row.get('servings')) else None,
                # Пустые поля для совместимости (можно будет заполнить позже)
                steps=[],
                description=None,
                category=None,
                cuisine=None,
                complexity=None,
                image_url=None
            )
            db.add(recipe)
            count += 1
            
            if count % 1000 == 0:
                print(f"Загружено {count} рецептов...")
                db.commit()
                
        except Exception as e:
            print(f"Ошибка при загрузке рецепта: {e}")
            continue
    
    db.commit()
    db.close()
    print(f"✅ Загружено {count} рецептов!")

if __name__ == "__main__":
    load_recipes()