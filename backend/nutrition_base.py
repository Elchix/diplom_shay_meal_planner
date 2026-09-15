# nutrition_base.py
# Справочник продуктов с КБЖУ на 100 г

PRODUCTS_BASE = {
    # ===== ОВОЩИ =====
    'картофель': {'calories': 77, 'protein': 2.0, 'fat': 0.1, 'carbs': 17.0},
    'картошка': {'calories': 77, 'protein': 2.0, 'fat': 0.1, 'carbs': 17.0},
    'морковь': {'calories': 41, 'protein': 0.9, 'fat': 0.2, 'carbs': 9.6},
    'морковка': {'calories': 41, 'protein': 0.9, 'fat': 0.2, 'carbs': 9.6},
    'лук': {'calories': 40, 'protein': 1.1, 'fat': 0.1, 'carbs': 9.3},
    'лук репчатый': {'calories': 40, 'protein': 1.1, 'fat': 0.1, 'carbs': 9.3},
    'чеснок': {'calories': 149, 'protein': 6.4, 'fat': 0.5, 'carbs': 33.1},
    'свекла': {'calories': 43, 'protein': 1.6, 'fat': 0.1, 'carbs': 9.6},
    'капуста': {'calories': 25, 'protein': 1.3, 'fat': 0.1, 'carbs': 5.8},
    'капуста белокочанная': {'calories': 25, 'protein': 1.3, 'fat': 0.1, 'carbs': 5.8},
    'огурцы': {'calories': 15, 'protein': 0.8, 'fat': 0.1, 'carbs': 3.6},
    'огурец': {'calories': 15, 'protein': 0.8, 'fat': 0.1, 'carbs': 3.6},
    'помидоры': {'calories': 18, 'protein': 0.9, 'fat': 0.2, 'carbs': 3.9},
    'томат': {'calories': 18, 'protein': 0.9, 'fat': 0.2, 'carbs': 3.9},
    'перец': {'calories': 26, 'protein': 1.0, 'fat': 0.3, 'carbs': 6.0},
    'перец болгарский': {'calories': 26, 'protein': 1.0, 'fat': 0.3, 'carbs': 6.0},
    'кабачок': {'calories': 17, 'protein': 1.2, 'fat': 0.3, 'carbs': 3.4},
    'баклажан': {'calories': 25, 'protein': 1.0, 'fat': 0.1, 'carbs': 5.9},
    'тыква': {'calories': 26, 'protein': 1.0, 'fat': 0.1, 'carbs': 6.5},
    'грибы': {'calories': 22, 'protein': 2.1, 'fat': 0.5, 'carbs': 0.6},
    'шампиньоны': {'calories': 22, 'protein': 2.1, 'fat': 0.5, 'carbs': 0.6},
    'щавель': {'calories': 22, 'protein': 1.5, 'fat': 0.3, 'carbs': 3.2},
    'свекольная ботва': {'calories': 20, 'protein': 1.5, 'fat': 0.1, 'carbs': 4.0},
    'зелень': {'calories': 30, 'protein': 2.0, 'fat': 0.5, 'carbs': 5.0},
    'укроп': {'calories': 40, 'protein': 2.5, 'fat': 0.5, 'carbs': 7.0},
    'петрушка': {'calories': 36, 'protein': 2.5, 'fat': 0.5, 'carbs': 6.0},
    'салат': {'calories': 15, 'protein': 1.0, 'fat': 0.5, 'carbs': 2.0},
    'редис': {'calories': 20, 'protein': 1.0, 'fat': 0.1, 'carbs': 4.0},
    'сельдерей': {'calories': 16, 'protein': 1.5, 'fat': 0.2, 'carbs': 3.0},
    'кабачок': {'calories': 17, 'protein': 1.2, 'fat': 0.3, 'carbs': 3.4},
    'брокколи': {'calories': 34, 'protein': 2.8, 'fat': 0.4, 'carbs': 7.0},
    'цветная капуста': {'calories': 25, 'protein': 1.9, 'fat': 0.3, 'carbs': 5.0},
    
    # ===== КРУПЫ, МАКАРОНЫ, МУКА =====
    'гречка': {'calories': 343, 'protein': 13.0, 'fat': 3.4, 'carbs': 71.0},
    'гречневая крупа': {'calories': 343, 'protein': 13.0, 'fat': 3.4, 'carbs': 71.0},
    'рис': {'calories': 130, 'protein': 2.7, 'fat': 0.3, 'carbs': 28.0},
    'рис белый': {'calories': 130, 'protein': 2.7, 'fat': 0.3, 'carbs': 28.0},
    'рис круглозерный': {'calories': 130, 'protein': 2.7, 'fat': 0.3, 'carbs': 28.0},
    'рис длиннозерный': {'calories': 130, 'protein': 2.7, 'fat': 0.3, 'carbs': 28.0},
    'макароны': {'calories': 131, 'protein': 5.0, 'fat': 1.1, 'carbs': 25.0},
    'паста': {'calories': 131, 'protein': 5.0, 'fat': 1.1, 'carbs': 25.0},
    'спагетти': {'calories': 131, 'protein': 5.0, 'fat': 1.1, 'carbs': 25.0},
    'овсянка': {'calories': 68, 'protein': 2.4, 'fat': 1.4, 'carbs': 12.0},
    'овсяные хлопья': {'calories': 68, 'protein': 2.4, 'fat': 1.4, 'carbs': 12.0},
    'крупа': {'calories': 340, 'protein': 12.0, 'fat': 3.0, 'carbs': 70.0},
    'мука': {'calories': 364, 'protein': 10.3, 'fat': 1.0, 'carbs': 76.3},
    'мука пшеничная': {'calories': 364, 'protein': 10.3, 'fat': 1.0, 'carbs': 76.3},
    'манная крупа': {'calories': 120, 'protein': 3.0, 'fat': 0.5, 'carbs': 25.0},
    'пшено': {'calories': 348, 'protein': 11.5, 'fat': 3.3, 'carbs': 69.3},
    'перловка': {'calories': 320, 'protein': 9.3, 'fat': 1.1, 'carbs': 73.7},
    'ячневая крупа': {'calories': 320, 'protein': 9.3, 'fat': 1.1, 'carbs': 73.7},
    'кукурузная крупа': {'calories': 330, 'protein': 8.3, 'fat': 1.2, 'carbs': 75.0},
    'горох': {'calories': 81, 'protein': 5.0, 'fat': 0.5, 'carbs': 14.0},
    'чечевица': {'calories': 116, 'protein': 9.0, 'fat': 0.4, 'carbs': 20.0},
    'фасоль': {'calories': 95, 'protein': 6.7, 'fat': 0.3, 'carbs': 17.0},
    'нут': {'calories': 139, 'protein': 8.9, 'fat': 2.6, 'carbs': 19.0},
    
    # ===== МЯСО И ПТИЦА =====
    'курица': {'calories': 165, 'protein': 20.0, 'fat': 10.0, 'carbs': 0.0},
    'куриное филе': {'calories': 110, 'protein': 23.0, 'fat': 1.2, 'carbs': 0.0},
    'куриная грудка': {'calories': 110, 'protein': 23.0, 'fat': 1.2, 'carbs': 0.0},
    'куриное бедро': {'calories': 180, 'protein': 18.0, 'fat': 12.0, 'carbs': 0.0},
    'куриный фарш': {'calories': 150, 'protein': 18.0, 'fat': 8.0, 'carbs': 0.0},
    'свинина': {'calories': 242, 'protein': 16.0, 'fat': 20.0, 'carbs': 0.0},
    'свиной фарш': {'calories': 250, 'protein': 17.0, 'fat': 20.0, 'carbs': 0.0},
    'говядина': {'calories': 250, 'protein': 18.0, 'fat': 20.0, 'carbs': 0.0},
    'говяжий фарш': {'calories': 250, 'protein': 17.0, 'fat': 20.0, 'carbs': 0.0},
    'телятина': {'calories': 120, 'protein': 20.0, 'fat': 4.0, 'carbs': 0.0},
    'баранина': {'calories': 240, 'protein': 16.0, 'fat': 20.0, 'carbs': 0.0},
    'фарш': {'calories': 250, 'protein': 17.0, 'fat': 20.0, 'carbs': 0.0},
    'ветчина': {'calories': 145, 'protein': 15.0, 'fat': 9.0, 'carbs': 1.0},
    'колбаса': {'calories': 250, 'protein': 12.0, 'fat': 22.0, 'carbs': 1.0},
    'колбаса вареная': {'calories': 250, 'protein': 12.0, 'fat': 22.0, 'carbs': 1.0},
    'сосиски': {'calories': 220, 'protein': 10.0, 'fat': 20.0, 'carbs': 2.0},
    'шницель': {'calories': 200, 'protein': 15.0, 'fat': 15.0, 'carbs': 5.0},
    'мясо': {'calories': 200, 'protein': 18.0, 'fat': 14.0, 'carbs': 0.0},
    'индейка': {'calories': 140, 'protein': 20.0, 'fat': 6.0, 'carbs': 0.0},
    'куропатка': {'calories': 120, 'protein': 20.0, 'fat': 4.0, 'carbs': 0.0},
    'утка': {'calories': 300, 'protein': 16.0, 'fat': 26.0, 'carbs': 0.0},
    
    # ===== РЫБА =====
    'рыба': {'calories': 150, 'protein': 20.0, 'fat': 7.0, 'carbs': 0.0},
    'лосось': {'calories': 220, 'protein': 20.0, 'fat': 15.0, 'carbs': 0.0},
    'семга': {'calories': 220, 'protein': 20.0, 'fat': 15.0, 'carbs': 0.0},
    'треска': {'calories': 70, 'protein': 17.0, 'fat': 0.5, 'carbs': 0.0},
    'минтай': {'calories': 72, 'protein': 16.0, 'fat': 1.0, 'carbs': 0.0},
    'сельдь': {'calories': 160, 'protein': 17.0, 'fat': 10.0, 'carbs': 0.0},
    'скумбрия': {'calories': 200, 'protein': 18.0, 'fat': 14.0, 'carbs': 0.0},
    'щука': {'calories': 84, 'protein': 18.0, 'fat': 1.0, 'carbs': 0.0},
    'окунь': {'calories': 100, 'protein': 18.0, 'fat': 3.0, 'carbs': 0.0},
    'камбала': {'calories': 90, 'protein': 16.0, 'fat': 3.0, 'carbs': 0.0},
    'карп': {'calories': 120, 'protein': 16.0, 'fat': 6.0, 'carbs': 0.0},
    'форель': {'calories': 150, 'protein': 20.0, 'fat': 7.0, 'carbs': 0.0},
    
    # ===== МОЛОЧНОЕ =====
    'молоко': {'calories': 60, 'protein': 3.2, 'fat': 3.2, 'carbs': 4.8},
    'творог': {'calories': 120, 'protein': 15.0, 'fat': 5.0, 'carbs': 2.0},
    'сыр': {'calories': 350, 'protein': 25.0, 'fat': 28.0, 'carbs': 1.0},
    'сыр твердый': {'calories': 350, 'protein': 25.0, 'fat': 28.0, 'carbs': 1.0},
    'сметана': {'calories': 200, 'protein': 3.0, 'fat': 20.0, 'carbs': 3.0},
    'сливки': {'calories': 200, 'protein': 3.0, 'fat': 20.0, 'carbs': 3.0},
    'масло сливочное': {'calories': 750, 'protein': 1.0, 'fat': 82.0, 'carbs': 1.0},
    'кефир': {'calories': 50, 'protein': 3.0, 'fat': 2.5, 'carbs': 4.0},
    'йогурт': {'calories': 60, 'protein': 4.0, 'fat': 3.0, 'carbs': 5.0},
    'ряженка': {'calories': 80, 'protein': 3.0, 'fat': 4.0, 'carbs': 5.0},
    'простокваша': {'calories': 60, 'protein': 3.0, 'fat': 3.0, 'carbs': 4.0},
    'сгущенное молоко': {'calories': 320, 'protein': 7.0, 'fat': 8.0, 'carbs': 55.0},
    'масло': {'calories': 750, 'protein': 1.0, 'fat': 82.0, 'carbs': 1.0},
    'сливочное масло': {'calories': 750, 'protein': 1.0, 'fat': 82.0, 'carbs': 1.0},
    
    # ===== ЯЙЦА =====
    'яйца': {'calories': 155, 'protein': 13.0, 'fat': 11.0, 'carbs': 1.1},
    'яйцо': {'calories': 155, 'protein': 13.0, 'fat': 11.0, 'carbs': 1.1},
    'яичный белок': {'calories': 52, 'protein': 11.0, 'fat': 0.2, 'carbs': 1.0},
    'яичный желток': {'calories': 320, 'protein': 16.0, 'fat': 27.0, 'carbs': 3.5},
    
    # ===== ХЛЕБ И ВЫПЕЧКА =====
    'хлеб': {'calories': 265, 'protein': 9.0, 'fat': 3.0, 'carbs': 50.0},
    'хлеб белый': {'calories': 265, 'protein': 9.0, 'fat': 3.0, 'carbs': 50.0},
    'хлеб черный': {'calories': 200, 'protein': 8.0, 'fat': 1.0, 'carbs': 40.0},
    'батон': {'calories': 260, 'protein': 8.0, 'fat': 2.0, 'carbs': 52.0},
    'булка': {'calories': 260, 'protein': 8.0, 'fat': 2.0, 'carbs': 52.0},
    'сухари': {'calories': 400, 'protein': 12.0, 'fat': 1.0, 'carbs': 85.0},
    'панировочные сухари': {'calories': 400, 'protein': 12.0, 'fat': 1.0, 'carbs': 85.0},
    'лаваш': {'calories': 270, 'protein': 8.0, 'fat': 1.0, 'carbs': 55.0},
    'пирог': {'calories': 300, 'protein': 5.0, 'fat': 15.0, 'carbs': 40.0},
    'бутерброд': {'calories': 250, 'protein': 8.0, 'fat': 10.0, 'carbs': 30.0},
    
    # ===== СЛАДОСТИ =====
    'сахар': {'calories': 400, 'protein': 0.0, 'fat': 0.0, 'carbs': 100.0},
    'сахарный песок': {'calories': 400, 'protein': 0.0, 'fat': 0.0, 'carbs': 100.0},
    'мёд': {'calories': 300, 'protein': 0.5, 'fat': 0.0, 'carbs': 80.0},
    'шоколад': {'calories': 550, 'protein': 5.0, 'fat': 35.0, 'carbs': 55.0},
    'варенье': {'calories': 250, 'protein': 0.5, 'fat': 0.0, 'carbs': 65.0},
    'джем': {'calories': 250, 'protein': 0.5, 'fat': 0.0, 'carbs': 65.0},
    'печенье': {'calories': 450, 'protein': 6.0, 'fat': 20.0, 'carbs': 65.0},
    'пряники': {'calories': 350, 'protein': 5.0, 'fat': 10.0, 'carbs': 70.0},
    
    # ===== МАСЛА И ЖИРЫ =====
    'масло растительное': {'calories': 900, 'protein': 0.0, 'fat': 100.0, 'carbs': 0.0},
    'подсолнечное масло': {'calories': 900, 'protein': 0.0, 'fat': 100.0, 'carbs': 0.0},
    'оливковое масло': {'calories': 900, 'protein': 0.0, 'fat': 100.0, 'carbs': 0.0},
    'майонез': {'calories': 600, 'protein': 1.0, 'fat': 65.0, 'carbs': 5.0},
    
    # ===== НАПИТКИ =====
    'вода': {'calories': 0, 'protein': 0.0, 'fat': 0.0, 'carbs': 0.0},
    'сок': {'calories': 50, 'protein': 0.5, 'fat': 0.1, 'carbs': 12.0},
    'компот': {'calories': 60, 'protein': 0.2, 'fat': 0.1, 'carbs': 15.0},
    'морс': {'calories': 50, 'protein': 0.5, 'fat': 0.1, 'carbs': 12.0},
    'квас': {'calories': 30, 'protein': 0.2, 'fat': 0.0, 'carbs': 7.0},
    'лимонад': {'calories': 40, 'protein': 0.0, 'fat': 0.0, 'carbs': 10.0},
    
    # ===== ФРУКТЫ И ЯГОДЫ =====
    'яблоко': {'calories': 52, 'protein': 0.3, 'fat': 0.2, 'carbs': 14.0},
    'яблоки': {'calories': 52, 'protein': 0.3, 'fat': 0.2, 'carbs': 14.0},
    'банан': {'calories': 89, 'protein': 1.1, 'fat': 0.3, 'carbs': 23.0},
    'бананы': {'calories': 89, 'protein': 1.1, 'fat': 0.3, 'carbs': 23.0},
    'апельсин': {'calories': 47, 'protein': 0.9, 'fat': 0.1, 'carbs': 12.0},
    'лимон': {'calories': 29, 'protein': 0.9, 'fat': 0.2, 'carbs': 9.0},
    'груша': {'calories': 57, 'protein': 0.4, 'fat': 0.1, 'carbs': 15.0},
    'виноград': {'calories': 69, 'protein': 0.6, 'fat': 0.2, 'carbs': 18.0},
    'клубника': {'calories': 32, 'protein': 0.7, 'fat': 0.3, 'carbs': 8.0},
    'малина': {'calories': 52, 'protein': 1.2, 'fat': 0.6, 'carbs': 12.0},
    'смородина': {'calories': 60, 'protein': 1.0, 'fat': 0.2, 'carbs': 15.0},
    'брусника': {'calories': 50, 'protein': 0.6, 'fat': 0.1, 'carbs': 12.0},
    'чернослив': {'calories': 240, 'protein': 2.2, 'fat': 0.4, 'carbs': 63.0},
    'изюм': {'calories': 300, 'protein': 3.0, 'fat': 0.5, 'carbs': 75.0},
    
    # ===== ОРЕХИ =====
    'грецкий орех': {'calories': 654, 'protein': 15.0, 'fat': 65.0, 'carbs': 14.0},
    'миндаль': {'calories': 579, 'protein': 21.0, 'fat': 50.0, 'carbs': 22.0},
    'арахис': {'calories': 567, 'protein': 26.0, 'fat': 49.0, 'carbs': 16.0},
    'фундук': {'calories': 628, 'protein': 15.0, 'fat': 61.0, 'carbs': 17.0},
    'кешью': {'calories': 553, 'protein': 18.0, 'fat': 44.0, 'carbs': 30.0},
    'семечки': {'calories': 580, 'protein': 20.0, 'fat': 50.0, 'carbs': 15.0},
    'тыквенные семечки': {'calories': 580, 'protein': 20.0, 'fat': 50.0, 'carbs': 15.0},
    
    # ===== СОУСЫ, ПРИПРАВЫ =====
    'томатная паста': {'calories': 80, 'protein': 4.0, 'fat': 0.5, 'carbs': 16.0},
    'томатный соус': {'calories': 80, 'protein': 4.0, 'fat': 0.5, 'carbs': 16.0},
    'кетчуп': {'calories': 80, 'protein': 4.0, 'fat': 0.5, 'carbs': 16.0},
    'соус соевый': {'calories': 50, 'protein': 5.0, 'fat': 0.0, 'carbs': 10.0},
    'горчица': {'calories': 66, 'protein': 4.0, 'fat': 3.0, 'carbs': 6.0},
    'уксус': {'calories': 20, 'protein': 0.0, 'fat': 0.0, 'carbs': 5.0},
    
    # ===== ОСТАЛЬНОЕ =====
    'соль': {'calories': 0, 'protein': 0.0, 'fat': 0.0, 'carbs': 0.0},
    'перец': {'calories': 20, 'protein': 1.0, 'fat': 0.5, 'carbs': 4.0},
    'специи': {'calories': 20, 'protein': 1.0, 'fat': 0.5, 'carbs': 4.0},
    'бульон': {'calories': 10, 'protein': 1.0, 'fat': 0.5, 'carbs': 0.5},
    'желатин': {'calories': 330, 'protein': 85.0, 'fat': 0.0, 'carbs': 0.0},
    'дрожжи': {'calories': 320, 'protein': 35.0, 'fat': 5.0, 'carbs': 35.0},
    'сухари панировочные': {'calories': 400, 'protein': 12.0, 'fat': 1.0, 'carbs': 85.0},
    'топленое масло': {'calories': 750, 'protein': 1.0, 'fat': 82.0, 'carbs': 1.0},
}

def get_nutrition(product_name):
    """
    Возвращает КБЖУ для продукта.
    Если продукт не найден точно, ищет частичное совпадение.
    Если ничего не найдено — возвращает средние значения.
    """
    if not product_name:
        return {'calories': 50, 'protein': 2.0, 'fat': 2.0, 'carbs': 5.0}
    
    product_name = product_name.lower().strip()
    
    # 1. Точное совпадение
    if product_name in PRODUCTS_BASE:
        return PRODUCTS_BASE[product_name]
    
    # 2. Частичное совпадение (ключ в названии или название в ключе)
    for key in PRODUCTS_BASE:
        if key in product_name or product_name in key:
            return PRODUCTS_BASE[key]
    
    # 3. Если ничего не найдено — возвращаем средние значения
    return {'calories': 50, 'protein': 2.0, 'fat': 2.0, 'carbs': 5.0}