import json
import os
from database import SessionLocal
from models import Recipe

def parse_time(time_str):
    """Преобразует строку времени в минуты"""
    if not time_str:
        return 0
    minutes = 0
    parts = time_str.split()
    for i, part in enumerate(parts):
        if part in ['час', 'ч'] and i > 0:
            minutes += int(parts[i-1]) * 60
        elif part in ['минут', 'мин'] and i > 0:
            minutes += int(parts[i-1])
    return minutes

def load_russian_recipes(json_folder="russian-recipes/storage/recipes"):
    """
    Загружает русские рецепты из JSON-файлов в базу данных
    """
    db = SessionLocal()
    count = 0
    errors = []
    
    print(f"🔍 Ищем JSON-файлы в папке: {json_folder}")
    
    # Проходим по всем папкам и файлам
    for root, dirs, files in os.walk(json_folder):
        for filename in files:
            if not filename.endswith('.json'):
                continue
            
            filepath = os.path.join(root, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                ingredients = []
                servings = 2
                for group in data.get('ingredients', []):
                    header = group.get('name') or ''
                    import re
                    m = re.search(r'(\d+)', header)
                    if m:
                        servings = int(m.group(1))
                    for item in group.get('list', []):
                        if item.get('name'):
                            ingredients.append({
                                "name": item['name'],
                                "amount": item.get('value'),
                                "unit": item.get('type') or '',
                                "notes": item.get('notes') or '',
                            })

                steps = []
                for step in data.get('instruction', []):
                    if step.get('text'):
                        steps.append({"text": step['text'], "image": step.get('photo') or step.get('image')})

                difficulty = data.get('difficulty') or 'средне'
                if 'низк' in str(difficulty).lower() or 'легк' in str(difficulty).lower():
                    difficulty = 'легко'
                elif 'высок' in str(difficulty).lower() or 'сложн' in str(difficulty).lower():
                    difficulty = 'сложно'
                else:
                    difficulty = 'средне'

                cook = parse_time(data.get('cooktime', ''))
                prep = parse_time(data.get('preparetime', '') or '')
                recipe = Recipe(
                    name=data.get('title', 'Без названия')[:255],
                    description=data.get('description', ''),
                    ingredients=ingredients,
                    steps=steps,
                    category=data.get('category', ''),
                    cuisine=data.get('cuisine', ''),
                    complexity=difficulty,
                    cook_time=cook,
                    prep_time=prep,
                    total_time=cook + prep,
                    servings=servings,
                    image_url=data.get('poster', ''),
                    video_url=data.get('video') or None,
                    url=data.get('source'),
                    calories=0,
                    protein=0,
                    fat=0,
                    carbs=0,
                )
                
                db.add(recipe)
                count += 1
                
                if count % 100 == 0:
                    print(f"📥 Загружено {count} рецептов...")
                    db.commit()
                    
            except json.JSONDecodeError as e:
                errors.append(f"❌ Ошибка JSON в {filepath}: {e}")
            except Exception as e:
                errors.append(f"❌ Ошибка в {filepath}: {e}")
                continue
    
    # Финальный commit
    db.commit()
    db.close()
    
    print(f"\n✅ УСПЕШНО ЗАГРУЖЕНО: {count} русских рецептов!")
    
    if errors:
        print(f"\n⚠️ ОШИБОК: {len(errors)}")
        for err in errors[:5]:
            print(f"  {err}")

if __name__ == "__main__":
    load_russian_recipes()