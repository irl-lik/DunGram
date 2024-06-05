import sqlite3
import json
import telebot
from telebot import types
import time
import datetime
import logging
from dotenv import load_dotenv, find_dotenv
import os
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
)
'''

c.executescript(script)

conn.commit()
conn.close()

@bot.message_handler(func=lambda message: message.date <= start_time)
def handle_old_updates(message):
    pass


def dealer(call):
    if call.from_user.id != int(call.data.split(':')[1]):
        bot.answer_callback_query(callback_query_id=call.id, text="Вы не можете взаимодействовать не со своей кнопкой!")
        return
    else:
        conn = sqlite3.connect('DunGram.db')
        c = conn.cursor()

        # Получаем все предметы из инвентаря пользователя
        c.execute("SELECT * FROM InventorySlots WHERE UserId = ?", (call.from_user.id,))
        inventory = c.fetchall()
        conn.close()
        items_available_for_sale = False  # Переменная для отслеживания наличия предметов доступных для продажи
        if inventory:
            markup = types.InlineKeyboardMarkup()
            message_text = 'Доступно к продаже:'
            btn_back = types.InlineKeyboardButton(
                text="⬅️Назад",
                callback_data=f"town:{call.from_user.id}")
            for index, item in enumerate(inventory, start=1):
                conn = sqlite3.connect('DunGram.db') #item_data
                c = conn.cursor()
                c.execute("SELECT ItemData FROM Items WHERE ItemId =?", (item[2],))
                item_data = json.loads(c.fetchone()[0])
                conn.close()
                if item_data.get("cost") is not None and item_data["cost"] > 0 and item[3] != 0:
                    total_cost = item_data["cost"] * item[3]
                    cost_format = count_formatter(total_cost, ['изумруд', 'изумруда', 'изумрудов'])
                    message_text += f'\n{index}. {get_item_name(item[2])}({item[3]}шт.) : {total_cost} {cost_format}'
                    items_available_for_sale = True  # Помечаем, что найден предмет доступный для продажи
                    btn = types.InlineKeyboardButton(text=f"{get_item_name(item[2])}", callback_data=f"dealer_sell:{call.from_user.id}:{item[2]}")
                    markup.row(btn)
            if not items_available_for_sale:
                message_text = "Нет предметов доступных на продажу."
                bot.send_message(call.message.chat.id, text=message_text)
            markup.row(btn_back)
            bot.send_message(call.message.chat.id, text=message_text, reply_markup=markup)
        else:
            bot.send_message(call.message.chat.id, "Нет предметов доступных на продажу.")

def dealer_sell(call):
    if call.from_user.id != int(call.data.split(':')[1]):
        bot.answer_callback_query(callback_query_id=call.id, text="Вы не можете взаимодействовать не со своей кнопкой!")
        return
    user_id, item_id = call.data.split(':')[1:3]
    conn = sqlite3.connect('DunGram.db')
    c = conn.cursor()
    c.execute("SELECT * FROM InventorySlots WHERE UserId = ? AND ItemId = ?", (user_id, item_id))
    item = c.fetchone()
    conn.close()

    if item is None:
        bot.answer_callback_query(callback_query_id=call.id, text="Вы не можете продать предмет, которого у вас нет в инвентаре!")
        return

    # Проверяем, существует ли запись о пользователе в таблице ProfileBalance
    conn = sqlite3.connect('DunGram.db')
    c = conn.cursor()
    c.execute("SELECT * FROM ProfileBalance WHERE UserId = ?", (user_id,))
    user_balance = c.fetchone()
    if user_balance is None:
        # Если запись отсутствует, добавляем новую запись с начальным балансом
        c.execute("INSERT INTO ProfileBalance (UserId, Balance) VALUES (?, ?)", (user_id, 0))  # Начальный баланс равен 0
        conn.commit()
    conn.close()

    # Получаем данные о предмете
    item_data = json.loads(get_item_data(item[2]))

    # Проверяем, может ли предмет быть продан
    if item_data["cost"] is None or item_data["cost"] <= 0:
        bot.answer_callback_query(callback_query_id=call.id, text="Этот предмет не может быть продан!")
        return

    total_count = min(item[3], 64)  # Приводим количество к максимальной продажной порции (64)
    total_cost = item_data["cost"] * total_count

    conn = sqlite3.connect('DunGram.db')
    c = conn.cursor()
    c.execute("UPDATE InventorySlots SET ItemCount = ItemCount - ? WHERE UserId = ? AND ItemId = ?", (total_count, user_id, item_id))
    c.execute("UPDATE ProfileBalance SET Balance = Balance + ? WHERE UserId = ?", (total_cost, user_id))
    conn.commit()
    conn.close()

    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(text="Вернуться", callback_data=f"dealer:{call.from_user.id}"))
    bot.edit_message_text(chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text=f"Вы продали {get_item_name(item_id)} ({total_count} шт.) за {total_cost} монет!",
                        reply_markup=markup)