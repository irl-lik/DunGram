import sqlite3
import json
from typing import Union

def profile_exists(user_id: int) -> bool:
    conn = sqlite3.connect('DunGram.db')
    c = conn.cursor()
    c.execute("SELECT * FROM Profiles WHERE UserId = ?", (user_id,))
    if c.fetchone() is None:
        conn.close()
        return False
    else:
        conn.close()
        return True

def add_item_to_inventory(user_id: int, item_id: int, count: int) -> Union[str, bool]:
    conn = sqlite3.connect('DunGram.db')
    c = conn.cursor()
    c.execute('SELECT ItemCount FROM InventorySlots WHERE UserId=? AND ItemId=?', (user_id, item_id))
    row = c.fetchone()
    conn.commit()
    heal_potions = 0
    heal_ids = [21, 22, 23, 24]

    for heal_id in heal_ids:
        c.execute('SELECT ItemCount FROM InventorySlots WHERE UserID=? AND ItemId=?', (user_id, heal_id))
        result = c.fetchone()
        if result is not None:
            heal_potions += result[0]

    if heal_potions >= 20:
        return False

    if row:
        new_count = row[0] + count  # Добавляем к текущему количеству
        return f'UPDATE InventorySlots SET ItemCount={new_count} WHERE UserId={user_id} AND ItemId={item_id}'
    else:
        return f'INSERT INTO InventorySlots (UserId, ItemId, ItemCount) VALUES ({user_id}, {item_id}, {count})'

def get_item_name(item_id: int) -> str:
    conn = sqlite3.connect('DunGram.db')
    c = conn.cursor()
    c.execute("SELECT ItemName FROM Items WHERE ItemId = ?", (item_id,))
    item = c.fetchone()
    if item is not None:
        item_name = item[0]  # Получаем название предмета по его ID
    else:
        item_name = "Неизвестный предмет"  # Или любое другое значение по умолчанию
    conn.close()
    return item_name

def get_item_data(item_id: int) -> str:
    conn = sqlite3.connect('DunGram.db')
    c = conn.cursor()
    c.execute("SELECT ItemData FROM Items WHERE ItemId = ?", (item_id,))
    item = c.fetchone()
    if item is not None:
        item_data = item[0]  # Получаем данные предмета по его ID
    else:
        item_data = "{data: 'None'}"
    conn.close()
    return item_data

def check_inventory(user_id: int, ingredient_list_json: str) -> bool:
    # Преобразование JSON-строки в объект Python
    ingredient_list = json.loads(ingredient_list_json)

    conn = sqlite3.connect('DunGram.db')
    c = conn.cursor()
    for ingredient in ingredient_list:
        item_id = ingredient[0]
        required_count = ingredient[1]
        # Проверяем, есть ли у пользователя достаточное количество данного ингредиента
        c.execute("SELECT ItemCount FROM InventorySlots WHERE UserId=? AND ItemId=?", (user_id, item_id))
        row = c.fetchone()
        if row is None or row[0] < required_count:
            conn.close()
            return False  # У пользователя недостаточно ингредиентов
    
    conn.close()
    return True  # У пользователя достаточно всех ингредиентов

def is_user_in_sortie(user_id:int) -> bool:
    conn = sqlite3.connect('DunGram.db')
    c = conn.cursor()
    c.execute("SELECT * FROM SortieData WHERE UserId = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result is not None

def add_to_sortie(user_id: int, enemy_id: int, user_data: dict, enemy_data: dict) -> bool:
    conn = sqlite3.connect('DunGram.db')
    c = conn.cursor()
    
    # Проверяем, есть ли уже запись о пользователе
    c.execute("SELECT * FROM SortieData WHERE UserId = ?", (user_id,))
    existing_entry = c.fetchone()
    if existing_entry:
        conn.close()
        return False  # Пользователь уже в стычке, возвращаем False

    # Вставляем новую запись о пользователе и его враге
    c.execute("INSERT INTO SortieData (UserId, EnemyId, UserData, EnemyData) VALUES (?, ?, ?, ?)",
            (user_id, enemy_id, json.dumps(user_data), json.dumps(enemy_data)))

    conn.commit()
    conn.close()
    return True  # Успешно добавлено в стычку, возвращаем True

def remove_from_sortie(user_id):
    conn = sqlite3.connect('DunGram.db')
    c = conn.cursor()
    c.execute("DELETE FROM SortieData WHERE UserId=?", (user_id,))
    conn.commit()
    conn.close()

def get_user_level(user_id:int) -> bool:
    try:
        # Подключение к базе данных
        conn = sqlite3.connect('DunGram.db')
        c = conn.cursor()
        c.execute("SELECT Level FROM Profiles WHERE UserId=?", (user_id,))
        user_level = c.fetchone()
        if user_level:
            return user_level[0]
        else:
            return 0  # Если пользователь не найден, возвращаем уровень 0
    except sqlite3.Error as e:
        print("Ошибка при работе с базой данных:", e)
        return 0  # В случае ошибки возвращаем уровень 0
    finally:
        if conn:
            conn.close()  # Закрываем соединение с базой данных

def get_user_exp(user_id:int) -> bool:
    try:
        # Подключение к базе данных
        conn = sqlite3.connect('DunGram.db')
        c = conn.cursor()
        c.execute("SELECT Experience FROM Profiles WHERE UserId=?", (user_id,))
        user_level = c.fetchone()
        if user_level:
            return user_level[0]
        else:
            return 0  # Если пользователь не найден, возвращаем уровень 0
    except sqlite3.Error as e:
        print("Ошибка при работе с базой данных:", e)
        return 0  # В случае ошибки возвращаем уровень 0
    finally:
        if conn:
            conn.close()  # Закрываем соединение с базой данных

def count_formatter(count: int, formats: list[str]):
    if count % 10 == 1 and count % 100 != 11:
        return formats[0]
    elif count % 10 >= 2 and count % 10 <= 4 and (count % 100 < 10 or count % 100 >= 20):
        return formats[1]
    else:
        return formats[2]