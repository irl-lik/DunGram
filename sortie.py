import sqlite3
import json
import telebot
from telebot import types
import time
import datetime
import logging
from dotenv import load_dotenv, find_dotenv
import os
import random
from components import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('telebot')
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

load_dotenv(find_dotenv())
bot = telebot.TeleBot(os.getenv('TOKEN'))
start_time = time.time()
conn = sqlite3.connect('DunGram.db')
c = conn.cursor()


script = '''
CREATE TABLE IF NOT EXISTS Users (
    UserId INTEGER PRIMARY KEY,
    RegistrationDate TEXT
);

CREATE TABLE IF NOT EXISTS Profiles (
    ProfileId INTEGER PRIMARY KEY,
    UserId INTEGER,
    Class TEXT,
    Level INTEGER,
    Experience INTEGER,
    FOREIGN KEY (UserId) REFERENCES Users(UserId)
);

CREATE TABLE IF NOT EXISTS InventorySlots (
    SlotId INTEGER PRIMARY KEY,
    UserId INTEGER,
    ItemId INTEGER,
    ItemCount INTEGER,
    FOREIGN KEY (UserId) REFERENCES Users(UserId),
    FOREIGN KEY (ItemId) REFERENCES Items(ItemId)
);

CREATE TABLE IF NOT EXISTS Items (
    ItemId INTEGER PRIMARY KEY,
    ItemName TEXT,
    ItemData TEXT
);

CREATE TABLE IF NOT EXISTS Recipes (
    ResultItemID INTEGER,
    RecipeClass INTEGER,
    Ingredients TEXT,
    ResultItemCount INTEGER
);

CREATE TABLE IF NOT EXISTS ProfileBalance (
    UserId INTEGER,
    Balance INTEGER,
    FOREIGN KEY (UserId) REFERENCES Users(UserId)
);

CREATE TABLE IF NOT EXISTS SortieData (
    BattleId INTEGER PRIMARY KEY,
    UserId INTEGER,
    EnemyId INTEGER,
    UserData TEXT,
    EnemyData TEXT
)
'''


c.executescript(script)

conn.commit()
conn.close()

@bot.message_handler(func=lambda message: message.date <= start_time)
def handle_old_updates(message):
    pass


def sortie(call):
    if call.from_user.id != int(call.data.split(':')[1]):
        bot.answer_callback_query(callback_query_id=call.id, text="Вы не можете взаимодействовать не со своей кнопкой!")
        return
    user_id = call.from_user.id
    text = (
        "Перед Вами развилка◀️🔼▶️!"
        "💭Выберите нужное направление💭:"
    )
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(
        text="Городские улицы", callback_data=f"sortie_streets:{user_id}")
    btn2 = types.InlineKeyboardButton(
        text="Заброшенные шахты", callback_data=f"sortie_caves:{user_id}")
    btn_back = types.InlineKeyboardButton(
        text="⬅️Назад", callback_data=f"town:{call.from_user.id}")
    markup.row(btn1)
    markup.row(btn2)
    markup.row(btn_back)
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=text,
        reply_markup=markup)

def sortie_streets(call):
    user_id = call.from_user.id
    if user_id != int(call.data.split(':')[1]):
        bot.answer_callback_query(callback_query_id=call.id, text="Вы не можете взаимодействовать не со своей кнопкой!")
        return
    user_level = get_user_level(user_id)
    if user_level < 1:
        bot.answer_callback_query(callback_query_id=call.id, text="У Вас недостаточно уровня!\n(Надо 1)")
        return
    markup = types.InlineKeyboardMarkup()
    btn_back = types.InlineKeyboardButton(
        text="⬅️Назад", callback_data=f"sortie:{call.from_user.id}")
    btn1 = types.InlineKeyboardButton(
        text="Продвинуться", callback_data=f"sortie_advance_streets:{user_id}:1")
    markup.row(btn1)
    markup.row(btn_back)

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="💥Вы начали вылазку💥",
        reply_markup=markup
    )


def sortie_advance_streets(call):
    user_id = call.from_user.id
    if user_id != int(call.data.split(':')[1]):
        bot.answer_callback_query(callback_query_id=call.id, text="Вы не можете взаимодействовать не со своей кнопкой!")
        return

    # Проверяем, находится ли пользователь уже в стычке
    if is_user_in_sortie(user_id):
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Вы уже участвуете в стычке. Дождитесь окончания текущего сражения или сбегите🏃"
        )
        return

    enemy_id = random.randint(1, 4)
    conn = sqlite3.connect('DunGram.db')
    c = conn.cursor()
    c.execute('SELECT * FROM SortieEnemies WHERE EnemyId=?', (enemy_id,))
    enemy = c.fetchone()
    enemy_name = enemy[1]
    enemy_base_data = json.loads(enemy[2])
    
    # Получаем данные о игроке (это заглушка)
    user_data = {"health": 20, "current_health": 20, "attack": 8, "DodgeChance": 0, "CriticalDamage": 25, 
                "moves": {'attack': 0, 'attack_cd': 2, 'abil1': 0, 'abil2_cd': 8,
                        'abil2': 0, 'abil2_cd': 5, 'abil3': 0, 'abil3_cd': 12,
                        'potion': 0, 'potion_cd': 2}}
    enemy_data = {key: int(value * random.uniform(0.9, 1.1)) for key, value in enemy_base_data.items()}
    enemy_data["current_health"] = enemy_data["health"]
    # Добавляем пользователя и его врага в таблицу SortieData
    add_to_sortie(user_id, enemy_id, user_data, enemy_data)

    # Отображаем информацию о столкновении и варианты действий
    markup = types.InlineKeyboardMarkup()
    btn_continue = types.InlineKeyboardButton(
        text="Продолжить", callback_data=f"sortie_continue:{user_id}")
    btn_escape = types.InlineKeyboardButton(
        text="Сбежать", callback_data=f"sortie_escape:{user_id}")
    markup.row(btn_continue)
    markup.row(btn_escape)
    user_moves = user_data["moves"]
    moves_text = "\n".join(
        move for move in user_moves if user_moves[move] > 0 and 'cd' not in move
            ) if any(
        user_moves[move] > 0 and 'cd' not in move for move in user_moves
            ) else 'Вы пока ничего не выбрали💬!'
    can_moves_text = "\n".join(move for move in user_moves if user_moves[move] == 0)
    text = (
        f"Стычка:\n\n"
        f"Вы {user_data['current_health']}/{user_data['health']}❤️\n\n"
        f"{enemy_name} {enemy_data['current_health']}/{enemy_data['health']}🖤\n"
        "————\n"
        f"{can_moves_text}\n"
        "Сбежать\n"
        "————\n\n"
        f"Ваши действия:\n"
        f"{moves_text}"
    )

    bot.send_message(
        chat_id=call.message.chat.id,
        text=text,
        reply_markup=markup
    )

def sortie_continue(call):
    user_id = call.from_user.id
    if user_id != int(call.data.split(':')[1]):
        bot.answer_callback_query(callback_query_id=call.id, text="Вы не можете взаимодействовать не со своей кнопкой!")
        return
    # Проверяем, находится ли пользователь уже в стычке
    if not is_user_in_sortie(user_id):
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Вы уже не участвуете в стычке. Найдите новое сражение"
        )
        return
    
    conn = sqlite3.connect('DunGram.db')
    try:
        c = conn.cursor()
        c.execute('SELECT * FROM SortieData WHERE UserId=?', (user_id,))
        conn.commit()
        sortie_data = c.fetchone()
        user_data = json.loads(sortie_data[3])
    except:
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Вы уже не участвуете ни в какой стычке. Найдите новое сражение"
        )
        return
    # enemy_data = json.loads(sortie_data[4])
    # enemy_id = sortie_data[2]
    user_moves = user_data["moves"]
    turn_player_damage, turn_enemy_damage = 0, 0
    for move in user_moves:
        if user_moves[move] > 0 and not 'cd' in move:
            if user_moves[move] == user_moves[move+'_cd']:
                turn_player_damage += 5 #Заглушка
            user_moves[move] -= 1
    user_data["moves"] = user_moves
    c.execute("UPDATE SortieData SET UserData =? WHERE UserId =?", (json.dumps(obj=user_data), user_id))
    conn.commit()
    conn.close()
    turn_enemy_damage += 5 #Заглушка
    bot.send_message(call.message.chat.id, text=f'Заглушка сработала, \nВаш урон: {turn_player_damage}\nУрон оппонента: {turn_enemy_damage}')


def sortie_end(message):
    # Проверяем, находится ли пользователь в стычке
    if not is_user_in_sortie(message.from_user.id):
        bot.send_message(
            chat_id=message.chat.id,
            text="Вы не участвуете в стычке. Начните новую для этого действия."
        )
        return
    remove_from_sortie(message.from_user.id)
    bot.send_message(
        chat_id=message.chat.id,
        text="Стычка завершена. Вы успешно покинули битву."
    )


def attack(message):
    # Проверяем, находится ли пользователь в стычке
    if not is_user_in_sortie(message.from_user.id):
        bot.send_message(
            chat_id=message.chat.id,
            text="Вы не участвуете в стычке. Начните новую для этого действия."
        )
        return
    conn = sqlite3.connect('DunGram.db')
    c = conn.cursor()
    c.execute("SELECT * FROM SortieData WHERE UserId =?", (message.from_user.id,))
    sortie_data = c.fetchone()
    user_data = json.loads(sortie_data[3])
    enemy_data = json.loads(sortie_data[4])
    enemy_id = sortie_data[2]
    c.execute('SELECT * FROM SortieEnemies WHERE EnemyId=?', (enemy_id,))
    enemy = c.fetchone()
    enemy_name = enemy[1]
    conn.commit()
    user_moves = user_data["moves"]
    if user_moves['attack'] == 0:
        user_moves['attack'] = 2
    elif user_moves['attack'] == 2:
        user_moves['attack'] = 0
    user_data["moves"] = user_moves
    c.execute("UPDATE SortieData SET UserData =? WHERE UserId =?", (json.dumps(user_data), message.from_user.id))
    conn.commit()
    conn.close()

    moves_text = "\n".join(
        move for move in user_moves if user_moves[move] > 0 and 'cd' not in move
            ) if any(
        user_moves[move] > 0 and 'cd' not in move for move in user_moves
            ) else 'Вы пока ничего не выбрали💬!'
    can_moves_text = "\n".join(move for move in user_moves if user_moves[move] == 0)
    if user_moves['attack'] in range(1, 2):
        moves_text += '\nНе удалось выбрать Атака,\nЗадержка не завершена'
    text = (
        f"Стычка:\n\n"
        f"Вы {user_data['current_health']}/{user_data['health']}❤️\n\n"
        f"{enemy_name} {enemy_data['current_health']}/{enemy_data['health']}🖤\n"
        "————\n"
        f"{can_moves_text}\n"
        "Сбежать\n"
        "————\n\n"
        f"Ваши действия:\n"
        f"{moves_text}"
    )

    markup = types.InlineKeyboardMarkup()
    btn_continue = types.InlineKeyboardButton(
        text="Продолжить", callback_data=f"sortie_continue:{message.from_user.id}")
    btn_escape = types.InlineKeyboardButton(
        text="Сбежать", callback_data=f"sortie_escape:{message.from_user.id}")
    markup.row(btn_continue)
    markup.row(btn_escape)

    bot.send_message(
        chat_id=message.chat.id,
        text=text,
        reply_markup=markup
    )