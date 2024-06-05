#''' # import sqlite3
# import json
# import telebot
# from dotenv import load_dotenv, find_dotenv
# import os

# load_dotenv(find_dotenv())
# bot = telebot.TeleBot(os.getenv('TOKEN'))

# @bot.message_handler(commands=['test'])
# def test(message):
#    bot.send_message(message.chat.id, message)

# bot.polling(none_stop=True)

# # def check_inventory(user_id: int, ingredient_list_json: str) -> bool:
# #     # Преобразование JSON-строки в объект Python
# #     ingredient_list = json.loads(ingredient_list_json)

# #     conn = sqlite3.connect('DunGram.db')
# #     c = conn.cursor()
# #     for ingredient in ingredient_list:
# #         item_id = ingredient[0]
# #         required_count = ingredient[1]
# #         # Проверяем, есть ли у пользователя достаточное количество данного ингредиента
# #         c.execute("SELECT ItemCount FROM InventorySlots WHERE UserId=? AND ItemId=?", (user_id, item_id))
# #         row = c.fetchone()
# #         if row is None or row[0] < required_count:
# #             conn.close()
# #             return False  # У пользователя недостаточно ингредиентов
    
# #     conn.close()
# #     return True  # У пользователя достаточно всех ингредиентов


# # print(check_inventory(1701803102, ('[[1, 1], [2, 1]]')))

# import json

# data_str = '''{"alchemist_item": true,
#'''# "blacksmith_item": false,
# "weapon": false,
# "armor": false,
# "cost": 1
# }'''
#'''# data_dict = json.loads(data_str)

# print(data_dict["cost"])

# import sqlite3
# import json
# import random
# import telebot
# from telebot import types
# from dotenv import load_dotenv
# import os

# # Загрузка переменных окружения
# load_dotenv()

# # Создание бота с использованием токена из переменных окружения
# bot = telebot.TeleBot(os.getenv('TOKEN'))

# # Подключение к базе данных
# conn = sqlite3.connect('test.db')
# c = conn.cursor()

# Создание таблиц в базе данных, если они не существуют
# script = '''
#'''# CREATE TABLE IF NOT EXISTS Items (
#     ItemId INTEGER PRIMARY KEY,
#     ItemName TEXT,
#     Effects TEXT
# );
# '''
#'''# c.executescript(script)
# conn.commit()
# conn.close()

# # Словарь с эффектами и диапазонами процентов
# item_effects_data = {
#     "Скорость Атаки": (5, 10),
#     "Оглушение": (10, 20),
#     "Шанс Крита": (15, 25),
#     "Урон Крита": (20, 30)
# }

# # Функция для генерации случайных эффектов и процентов для нового предмета
# def generate_item_effects():
#     item_effects = []
#     for _ in range(random.randint(1, 3)):
#         effect = random.choice(list(item_effects_data.keys()))
#         min_percentage, max_percentage = item_effects_data[effect]
#         percentage = random.randint(min_percentage, max_percentage)
#         item_effects.append({"effect": effect, "percentage": percentage})
#     return item_effects

# # Функция для создания нового меча с случайными эффектами и процентами
# def create_sword(user_id):
#     # Подключение к базе данных внутри функции
#     conn = sqlite3.connect('test.db')
#     c = conn.cursor()

#     effects = generate_item_effects()
#     sword_data = {"name": "Каменный Меч", "effects": effects}
#     c.execute("INSERT INTO Items (ItemName, Effects) VALUES (?, ?)", (sword_data["name"], json.dumps(sword_data['effects'])))
#     conn.commit()
    
#     # Закрытие соединения
#     conn.close()

# # Функция для использования меча игроком
# @bot.message_handler(commands=['use_sword'])
# def use_sword(message):
#     # Подключение к базе данных внутри функции
#     conn = sqlite3.connect('test.db')
#     c = conn.cursor()
#     c.execute("SELECT * FROM Items")
#     items = c.fetchall()
#     if not items:
#         bot.reply_to(message, "У вас нет мечей!")
#         return
#     sword_id = items[0][0]  # Предполагается, что игрок использует первый меч из своего инвентаря
#     effects = json.loads(items[0][2])
#     # Применяем эффекты к игроку
#     effects_str = '\n'.join([f"{effect['effect']}: {effect['percentage']}%" for effect in effects])
#     response = f"Вы использовали меч с эффектами:\n{effects_str}"
#     # Удаляем предмет из инвентаря игрока
#     c.execute("DELETE FROM Items WHERE ItemId = ?", (sword_id,))
#     conn.commit()
#     # Закрытие соединения
#     conn.close()
#     bot.reply_to(message, response)

# @bot.message_handler(commands=['show_sword'])
# def show_sword(message):
#     # Подключение к базе данных внутри функции
#     conn = sqlite3.connect('test.db')
#     c = conn.cursor()

#     c.execute("SELECT * FROM Items")
#     items = c.fetchall()
#     conn.commit()
#     conn.close()
#     if not items:
#         bot.reply_to(message, "У вас нет мечей!")
#         return
#     sword_id = items[0][0]  # Предполагается, что игрок использует первый меч из своего инвентаря
#     effects = json.loads(items[0][2])
#     # Применяем эффекты к игроку
#     effects_str = '\n'.join([f"{effect['effect']}: {effect['percentage']}%" for effect in effects])
#     response = f"Меч с эффектами:\n{effects_str}"
#     bot.reply_to(message, response)

# # Функция для обработки команды создания нового меча
# @bot.message_handler(commands=['create_sword'])
# def handle_create_sword(message):
#     create_sword(message.from_user.id)
#     bot.reply_to(message, "Вы получили новый меч!")

# # Запуск бота
# bot.polling()

# import sqlite3
# import json
# import random
# import telebot
# from telebot import types
# from dotenv import load_dotenv
# import os

# # Загрузка переменных окружения
# load_dotenv()

# # Создание бота с использованием токена из переменных окружения
# bot = telebot.TeleBot(os.getenv('TOKEN'))

# # Подключение к базе данных
# conn = sqlite3.connect('test.db')
# c = conn.cursor()

# script = """
# CREATE TABLE IF NOT EXISTS BattleData (
#     UserId INTEGER PRIMARY KEY,
#     isFighting BOOLEAN,
#     PlayerData TEXT,
#     Enemies TEXT
# )
# """
# c.execute(script)
# conn.commit()
# conn.close()

# # Функция для обновления данных игрока в базе данных
# def update_player_data(user_id, new_data):
#     conn = sqlite3.connect('test.db')
#     c = conn.cursor()
#     c.execute("UPDATE BattleData SET PlayerData = ? WHERE UserId = ?", (json.dumps(new_data), user_id))
#     conn.commit()
#     conn.close()

# # Функция для получения данных игрока из базы данных
# def get_player_data(user_id):
#     conn = sqlite3.connect('test.db')
#     c = conn.cursor()
#     c.execute("SELECT PlayerData FROM BattleData WHERE UserId = ?", (user_id,))
#     row = c.fetchone()
#     conn.close()
#     if row:
#         return json.loads(row[0])
#     else:
#         return None

# # Обработчик команды /test
# @bot.message_handler(commands=['test'])
# def test(message):
#     user_id = message.from_user.id
#     conn = sqlite3.connect('test.db')
#     c = conn.cursor()
#     c.execute("INSERT OR IGNORE INTO BattleData (UserId, isFighting, PlayerData, Enemies) VALUES (?, ?, ?, ?)", (user_id, False, "{}", "[]"))
#     conn.commit()
#     conn.close()
#     bot.reply_to(message, "Вы добавлены в базу данных и готовы к битве!")

# # Обработчик команды /status
# @bot.message_handler(commands=['status'])
# def status(message):
#     user_id = message.from_user.id
#     player_data = get_player_data(user_id)
#     if player_data and player_data.get("isFighting", False):
#         bot.reply_to(message, "Вы находитесь в бою!")
#     else:
#         bot.reply_to(message, "Вы не в бою.")

# # Обработчик команды /at
# @bot.message_handler(commands=['at'])
# def attack(message):
#     user_id = message.from_user.id
#     player_data = get_player_data(user_id)
#     if player_data and not player_data.get("attacked", False):
#         player_data["attacked"] = True
#         update_player_data(user_id, player_data)
#         bot.reply_to(message, "Вы готовитесь к атаке!")
#     else:
#         bot.reply_to(message, "Вы уже совершили атаку или не в бою.")

# # Обработчик команды /lev
# @bot.message_handler(commands=['lev'])
# def levitation(message):
#     user_id = message.from_user.id
#     player_data = get_player_data(user_id)
#     if player_data and not player_data.get("levitated", False):
#         player_data["levitated"] = True
#         update_player_data(user_id, player_data)
#         bot.reply_to(message, "Вы готовитесь использовать левитацию!")
#     else:
#         bot.reply_to(message, "Вы уже использовали левитацию или не в бою.")

# # Обработчик команды /aura
# @bot.message_handler(commands=['aura'])
# def aura(message):
#     user_id = message.from_user.id
#     player_data = get_player_data(user_id)
#     if player_data and not player_data.get("aura_used", False):
#         player_data["aura_used"] = True
#         update_player_data(user_id, player_data)
#         bot.reply_to(message, "Вы готовитесь использовать ауру!")
#     else:
#         bot.reply_to(message, "Вы уже использовали ауру или не в бою.")

# # Обработчик команды /commit
# @bot.message_handler(commands=['commit'])
# def commit(message):
#     user_id = message.from_user.id
#     player_data = get_player_data(user_id)
#     if player_data:
#         bot.reply_to(message, f"Данные игрока: {player_data}")
#     else:
#         bot.reply_to(message, "Вы не в бою или еще не добавлены в базу данных.")

# # Запуск бота
# bot.polling() '''


#'''# Обработчик команды /test
# @bot.message_handler(commands=['test'])
# def test(message):
#     user_id = message.from_user.id
#     conn = sqlite3.connect('test.db')
#     c = conn.cursor()
#     c.execute("INSERT OR IGNORE INTO BattleData (UserId, isFighting, PlayerData, Enemies) VALUES (?, ?, ?, ?)", (user_id, False, "{}", "[]"))
#     conn.commit()
#     conn.close()
#     bot.reply_to(message, "Вы добавлены в базу данных и готовы к битве!")

# @bot.message_handler(commands=['stt'])
# def stt(message):
#     user_id = message.from_user.id
#     conn = sqlite3.connect('test.db')
#     c = conn.cursor()
#     c.execute("SELECT isFighting FROM BattleData WHERE UserId=?", (user_id,))
#     conn.commit()
#     isFighting = c.fetchone()
#     if isFighting[0] is None:
#         bot.send_message(
#             chat_id=message.chat.id,
#             text="Вы не начали бота"
#         )
#     else:
#         c.execute("UPDATE BattleData SET isFighting = ? WHERE UserId = ?", (True, user_id))
#         conn.commit()
#         conn.close()
#         bot.send_message(
#             message.chat.id,
#             text="ВЫ начали бой"
#         )


# # Обработчик команды /status
# @bot.message_handler(commands=['status'])
# def status(message):
#     user_id = message.from_user.id
#     conn = sqlite3.connect('test.db')
#     c = conn.cursor()
#     c.execute("SELECT isFighting FROM BattleData WHERE UserId = ?", (user_id,))
#     row = c.fetchone()
#     if row and row[0]:
#         bot.reply_to(message, "Вы находитесь в бою!")
#     else:
#         bot.reply_to(message, "Вы не в бою.")

#     conn.close()

# # Обработчик команды /at
# @bot.message_handler(commands=['at'])
# def attack(message):
#     user_id = message.from_user.id
#     conn = sqlite3.connect('test.db')
#     c = conn.cursor()
#     c.execute("SELECT PlayerData FROM BattleData WHERE UserId = ?", (user_id,))
#     player_data_row = c.fetchone()
#     if player_data_row:
#         player_data = json.loads(player_data_row[0])
#         if not player_data.get("attacked", 0):
#             player_data["attacked"] = 2
#             c.execute("UPDATE BattleData SET PlayerData = ? WHERE UserId = ?", (json.dumps(player_data), user_id))
#             conn.commit()
#             bot.reply_to(message, "Вы готовитесь к атаке!")
#         else:
#             bot.reply_to(message, "Вы уже совершили атаку или не можете атаковать на этом ходу.")
#     else:
#         bot.reply_to(message, "Вы не в бою или еще не добавлены в базу данных.")
    
#     conn.close()

# # Обработчик команды /lev
# @bot.message_handler(commands=['lev'])
# def levitation(message):
#     user_id = message.from_user.id
#     conn = sqlite3.connect('test.db')
#     c = conn.cursor()
#     c.execute("SELECT PlayerData FROM BattleData WHERE UserId = ?", (user_id,))
#     player_data_row = c.fetchone()
#     if player_data_row:
#         player_data = json.loads(player_data_row[0])
#         if not player_data.get("levitated", 0):
#             player_data["levitated"] = 4
#             c.execute("UPDATE BattleData SET PlayerData = ? WHERE UserId = ?", (json.dumps(player_data), user_id))
#             conn.commit()
#             bot.reply_to(message, "Вы готовитесь использовать левитацию!")
#         else:
#             bot.reply_to(message, "Вы уже использовали левитацию или не можете ее использовать на этом ходу.")
#     else:
#         bot.reply_to(message, "Вы не в бою или еще не добавлены в базу данных.")
    
#     conn.close()

# # Обработчик команды /aura
# @bot.message_handler(commands=['aura'])
# def aura(message):
#     user_id = message.from_user.id
#     conn = sqlite3.connect('test.db')
#     c = conn.cursor()
#     c.execute("SELECT PlayerData FROM BattleData WHERE UserId = ?", (user_id,))
#     player_data_row = c.fetchone()
#     if player_data_row:
#         player_data = json.loads(player_data_row[0])
#         if not player_data.get("aura_used", 0):
#             player_data["aura_used"] = 8
#             c.execute("UPDATE BattleData SET PlayerData = ? WHERE UserId = ?", (json.dumps(player_data), user_id))
#             conn.commit()
#             bot.reply_to(message, "Вы готовитесь использовать ауру!")
#         else:
#             bot.reply_to(message, "Вы уже использовали ауру или не можете ее использовать на этом ходу.")
#     else:
#         bot.reply_to(message, "Вы не в бою или еще не добавлены в базу данных.")
    
#     conn.close()


# # Обработчик команды /commit
# @bot.message_handler(commands=['commit'])
# def commit(message):
#     user_id = message.from_user.id
#     conn = sqlite3.connect('test.db')
#     c = conn.cursor()
#     c.execute("SELECT PlayerData FROM BattleData WHERE UserId = ?", (user_id,))
#     conn.commit()
#     player_data_row = c.fetchone()
#     if player_data_row:
#         player_data = json.loads(player_data_row[0])
#         if player_data:
#             for key in player_data:
#                 if player_data[key] > 0:
#                     player_data[key] -= 1
#             c.execute("UPDATE BattleData SET PlayerData = ? WHERE UserId = ?", (json.dumps(player_data), user_id))
#             conn.commit()
#             bot.reply_to(message, f"Данные игрока: {player_data}")
#         else:
#             bot.reply_to(message, "Вы не в бою или еще не добавлены в базу данных.")
#     else:
#         bot.reply_to(message, "Вы не в бою или еще не добавлены в базу данных.")
    
#     conn.close()

# @bot.message_handler(commands=['end'])
# def end(message):
    # pass '''

# import sqlite3
# import json
# import random
# import telebot
# from telebot import types
# from dotenv import load_dotenv
# import os
# import time
import threading

# # Загрузка переменных окружения
# load_dotenv()

# # Создание бота с использованием токена из переменных окружения
# bot = telebot.TeleBot(os.getenv('TOKEN'))

def send(text):
    for i in range(10):
        print(text)

# @bot.message_handler(commands=['start'])
def start():
    thread = threading.Thread(target=send, args=('hello',))
    thread.start()
    for i in range(10):
        print('bye')
    thread.join()

start()
# # Запуск бота
# bot.polling(skip_pending=True)
