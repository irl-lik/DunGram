import sqlite3
import json
import telebot
from telebot import types
import time
import datetime
import random
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
);

CREATE TABLE IF NOT EXISTS CanumanQuest (
    QuestId INTEGER,
    UserId INTEGER PRIMARY KEY
)
'''


c.executescript(script)

conn.commit()
conn.close()

quests = {
        "1": ["Акварелька", "Пройдите паркур чтобы получить Наполеон🎂!\n\n❗️Каждый прыжок должен быть не ранее чем через 2 секунды, и не позднее 2,5 секунд❗️"],
        "2": False,
    }

def canuman(call):
    if call.from_user.id != int(call.data.split(':')[1]):
        bot.answer_callback_query(callback_query_id=call.id, text="Вы не можете взаимодействовать не со своей кнопкой!")
        return
    
    conn = sqlite3.connect('DunGram.db')
    c = conn.cursor()
    
    c.execute("SELECT * FROM CanumanQuest WHERE UserId = ?", (call.from_user.id,))
    user_quest = c.fetchone()
    
    if user_quest is None:
        c.execute("INSERT INTO CanumanQuest (QuestId, UserId) VALUES (?, ?)", (1, call.from_user.id))
        conn.commit()
    conn.close()
    if user_quest is not None:
        user_quest = user_quest[0]
    else:
        user_quest = 1
    
    markup = types.InlineKeyboardMarkup()
    if quests[str(user_quest)] is not False:
        message_text = ("Начните выполнять квесты от Восилия!\n"
                        f"Квест: {user_quest}\n"
                        f"{quests[str(user_quest)][1]}"
                        )
        btn1 = types.InlineKeyboardButton(
            text=f"{quests[str(user_quest)][0]}",
            callback_data=f"canuman_quest:{call.from_user.id}:{user_quest}:1")
        markup.row(btn1)
    else:
        message_text = ("Да, ты монстр!🔥\n"
                        "Возвращайся позже, в ближайшее время у меня нет для тебя квестов📜\n"
                        "И по секрету, если хочешь предложить свои квесты, то пиши разработчику🤫")
    btn_back = types.InlineKeyboardButton(
        text="⬅️Назад",
        callback_data=f"town:{call.from_user.id}"
    )
    markup.row(btn_back)
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=message_text,
        reply_markup=markup)
    
def canuman_quest(call):
    if call.from_user.id != int(call.data.split(':')[1]):
        bot.answer_callback_query(callback_query_id=call.id, text="Вы не можете взаимодействовать не со своей кнопкой!")
        return
    
    user_quest, user_progress = map(int, call.data.split(':')[2:4])
    if user_quest == 1:
        message_text = quests['1'][1]
        start_time = time.time()
        if (user_progress <= 10) and (user_progress > 1):
            start_time = float(call.data.split(':')[4])
        if user_progress <= 15:
            current_time = time.time()
            if ((current_time - start_time) > 2.5) or ((current_time - start_time) < 2):
            # if False:
                message_text += "\nВы оступились, начинайте заново!"
                user_progress = 1
            message_text += f'\nСовершите прыжок!\n\nЕщё осталось: {15-user_progress+1}/15'
            buttons = ["E", "E", "E", "E", "E"]
            correct_button_index = random.randint(0, 4)
            buttons[correct_button_index] = "S"
            markup = types.InlineKeyboardMarkup()
            for _ in buttons:
                if _ == "S":
                    btn = types.InlineKeyboardButton(text="✅", callback_data=f"canuman_quest:{call.from_user.id}:{user_quest}:{user_progress+1}:{time.time()}")
                else:
                    btn = types.InlineKeyboardButton(text="❌", callback_data=f"canuman_quest:{call.from_user.id}:{user_quest}:1:{time.time()}")
                markup.row(btn)
        else:
            message_text = "Поздравляем!🎉\nВы получили торт Наполеон!🎂"
            conn = sqlite3.connect('DunGram.db')
            c = conn.cursor()
            c.execute("UPDATE CanumanQuest SET QuestId = ? WHERE UserId = ?", (user_quest+1, call.from_user.id,))
            conn.commit()
            conn.close()
            markup = types.InlineKeyboardMarkup()
            btn_back = types.InlineKeyboardButton(
                text="⬅️Назад",
                callback_data=f"canuman:{call.from_user.id}"
            )
            btn_rmb = types.InlineKeyboardButton(
                text="ПКМ 🖱",
                callback_data="a"
            )
            markup.row(btn_rmb)
            markup.row(btn_back)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=message_text,
            reply_markup=markup)
