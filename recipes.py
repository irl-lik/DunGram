import sqlite3
import json

# Подключение к базе данных
conn = sqlite3.connect('DunGram.db')
cursor = conn.cursor()


# Создание таблицы для рецептов
cursor.execute('''CREATE TABLE IF NOT EXISTS Recipes (
                    ResultItemID INTEGER PRIMARY KEY,
                    RecipeClass INTEGER,
                    Ingredients TEXT,
                    ResultItemCount INTEGER
                )'''
)

recipes_data = [
    # ResultID   ResultClass  List[List[int]]   ResultItemCount
    (32, 4, [[20, 1], [12, 1]], 1), # Слабость I
    (33, 4, [[7, 1], [12, 1]], 1), # Замедление I
    (34, 4, [[32, 1], [17, 1]], 1), # Слабость II
    (35, 4, [[33, 1], [19, 2]], 1), # Замедление II
]

# Преобразование списка ингредиентов в JSON-строку
recipes_data_with_json = [(result_item_id, recipe_class, json.dumps(ingredients), result_item_count) 
                            for result_item_id, recipe_class, ingredients, result_item_count in recipes_data]

# Вставка данных о рецептах в таблицу
cursor.executemany("INSERT INTO Recipes (ResultItemID, RecipeClass, Ingredients, ResultItemCount) VALUES (?, ?, ?, ?)", recipes_data_with_json)

# Сохранение изменений и закрытие соединения
conn.commit()
conn.close()
