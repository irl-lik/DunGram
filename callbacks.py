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


def start_game(call):
    if call.from_user.id != int(call.data.split(':')[1]):
        bot.answer_callback_query(callback_query_id=call.id, text="Вы не можете взаимодействовать не со своей кнопкой!")
        return
    user_id = call.from_user.id
    if profile_exists(user_id):
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(
            text="Вылазка", callback_data=f"sortie:{user_id}")
        btn2 = types.InlineKeyboardButton(
            text="Подземелья", callback_data=f"dungeons:{user_id}")
        btn_back = types.InlineKeyboardButton(
            text="⬅️Назад", callback_data=f"main:{user_id}")
        markup.row(btn1, btn2)
        markup.row(btn_back)
        bot.send_message(call.message.chat.id, "Выберите режим⚔️:", reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id, "Вы не создали персонажа!")

def character(call):
    if call.from_user.id != int(call.data.split(':')[1]):
        bot.answer_callback_query(callback_query_id=call.id, text="Вы не можете взаимодействовать не со своей кнопкой!")
        return
    user_id = call.from_user.id
    if not profile_exists(user_id):
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(
            text="Воин 🛡", callback_data=f"select_warrior:{call.from_user.id}")
        btn2 = types.InlineKeyboardButton(
            text="Маг 🧙‍♂️", callback_data=f"select_wiz:{call.from_user.id}")
        btn3 = types.InlineKeyboardButton(
            text="Ассасин 🥷", callback_data=f"select_assasin:{call.from_user.id}")
        btn4 = types.InlineKeyboardButton(
            text="О классах 👑", callback_data=f"about_classes:{call.from_user.id}")
        markup.row(btn1, btn2, btn3)
        markup.row(btn4)
        bot.send_message(call.message.chat.id, "У Вас пока нет персонажа!\nВыберите класс:",
                        reply_markup=markup)
    else:
        conn = sqlite3.connect('DunGram.db')
        c = conn.cursor()
        c.execute("SELECT * FROM Profiles WHERE UserId =?", (user_id,))
        profile = c.fetchone()
        c.execute("SELECT * FROM Users WHERE UserId =?", (user_id,))
        user = c.fetchone()
        c.execute("SELECT Balance FROM ProfileBalance WHERE UserId = ?", (user_id,))
        balance = c.fetchone()
        c.execute("SELECT QuestId FROM CanumanQuest WHERE UserId = ?", (user_id,))
        quest = c.fetchone()
        balance = balance[0] if balance is not None else 0
        markup = types.InlineKeyboardMarkup()
        btn4 = types.InlineKeyboardButton(
            text="О классах 👑", callback_data=f"about_classes:{user_id}")
        markup.row(btn4)
        class_emoji = ""
        if profile[2] == "Воин":
            class_emoji = "🛡"
        elif profile[2] == "Маг":
            class_emoji = "🧙‍♂️"
        elif profile[2] == "Ассасин":
            class_emoji = "🥷"
        trophies = [
"Бонапарт",
]
        user_trophies = trophies[:quest[0]-1]
        if user_trophies:
            user_trophies_text = "Ваши титулы:" + "\n" + "\n".join(user_trophies) + "\n\n"
        else:
            user_trophies_text = "У Вас нет титулов\n\n"
        message_text = (
            f"Вас зовут: {user[1]}🔅\n"
            f"Ваш класс: {profile[2]}{class_emoji}\n"
            f"Уровень: {profile[3]}🆙\n"
            f"Опыт: {profile[4]}⚜️\n"
            f"Количество изумрудов: {balance}💎\n\n"
            f"{user_trophies_text}"
            f"Зарегистрирован: {user[2]}🕓"
        )
        bot.send_message(call.message.chat.id,
                        text=message_text,
                        reply_markup=markup,
                        )

def select_warrior(call):
    if call.from_user.id != int(call.data.split(':')[1]):
        bot.answer_callback_query(callback_query_id=call.id, text="Вы не можете взаимодействовать не со своей кнопкой!")
        return
    user_id = call.from_user.id
    username = call.from_user.username
    registration_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not profile_exists(user_id):
        conn = sqlite3.connect('DunGram.db')
        c = conn.cursor()
        c.execute("INSERT INTO Profiles (UserId, Class, Level, Experience) VALUES (?,?,?,?)",
                (user_id, "Воин", 1, 0))
        c.execute("INSERT INTO Users (UserID, Username, RegistrationDate) VALUES (?,?,?)",
                (user_id, username, registration_date))
        conn.commit()
        conn.close()
        bot.send_message(call.message.chat.id, "Вы выбрали класс Воина!")
    else:
        bot.send_message(call.message.chat.id, "Вы уже выбрали класс!")

def select_wiz(call):
    if call.from_user.id != int(call.data.split(':')[1]):
        bot.answer_callback_query(callback_query_id=call.id, text="Вы не можете взаимодействовать не со своей кнопкой!")
        return
    user_id = call.from_user.id
    username = call.from_user.username
    registration_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not profile_exists(user_id):
        conn = sqlite3.connect('DunGram.db')
        c = conn.cursor()
        c.execute("INSERT INTO Profiles (UserId, Class, Level, Experience) VALUES (?,?,?,?)",
                (user_id, "Маг", 1, 0))
        c.execute("INSERT INTO Users (UserID, Username, RegistrationDate) VALUES (?,?,?)",
                (user_id, username, registration_date))
        conn.commit()
        conn.close()
        bot.send_message(call.message.chat.id, "Вы выбрали класс Мага!")
    else:
        bot.send_message(call.message.chat.id, "Вы уже выбрали класс!")

def select_assasin(call):
    if call.from_user.id != int(call.data.split(':')[1]):
        bot.answer_callback_query(callback_query_id=call.id, text="Вы не можете взаимодействовать не со своей кнопкой!")
        return
    user_id = call.from_user.id
    username = call.from_user.username
    registration_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not profile_exists(user_id):
        conn = sqlite3.connect('DunGram.db')
        c = conn.cursor()
        c.execute("INSERT INTO Profiles (UserId, Class, Level, Experience) VALUES (?,?,?,?)",
                (user_id, "Ассасин", 1, 0))
        c.execute("INSERT INTO Users (UserID, Username, RegistrationDate) VALUES (?,?,?)",
                (user_id, username, registration_date))
        conn.commit()
        conn.close()
        bot.send_message(call.message.chat.id, "Вы выбрали класс Ассасина!")
    else:
        bot.send_message(call.message.chat.id, "Вы уже выбрали класс!")

def about_classes(call):
    if call.from_user.id != int(call.data.split(':')[1]):
        bot.answer_callback_query(callback_query_id=call.id, text="Вы не можете взаимодействовать не со своей кнопкой!")
        return
    foo = '''
<b>Воин 🛡:</b>
<i>Умелый воин, одинаково искусный как в защите, так и в нападении.</i>

<b>Маг 🧙‍♂️</b>
<i>Могущественный маг, атакующий врагов с безопасный дистанции.</i>

<b>Ассасин 🥷</b>
<i>Ловкий и скрытный убийца, наносящий молниеносные удары.</i>
'''
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(
        text="⬅️Назад", callback_data=f"character:{call.from_user.id}")
    markup.row(btn1)
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=foo,
        reply_markup=markup,
        parse_mode='HTML'
    )




def town(call):
    if call.from_user.id != int(call.data.split(':')[1]):
        bot.answer_callback_query(callback_query_id=call.id, text="Вы не можете взаимодействовать не со своей кнопкой!")
        return
    if not profile_exists(call.data.split(':')[1]):
        bot.send_message(call.message.chat.id, "Сперва создайте персонажа!")
        return 
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(
        text="Топ 🏆", callback_data=f"top:{call.from_user.id}")
    btn2 = types.InlineKeyboardButton(
        text="Подземелья 🪬", callback_data=f"enter_dungeon:{call.from_user.id}")
    btn3 = types.InlineKeyboardButton(
        text="Хранилище 📦", callback_data=f"storage:{call.from_user.id}")
    btn4 = types.InlineKeyboardButton(
        text="Путешественник 🤔", callback_data=f"crossprofile:{call.from_user.id}")
    btn5 = types.InlineKeyboardButton(
        text="Кузнец 🔨", callback_data=f"hammersmith:{call.from_user.id}")
    btn6 = types.InlineKeyboardButton(
        text="Алхимик 🧪", callback_data=f"alchemist:{call.from_user.id}")
    btn7 = types.InlineKeyboardButton(
        text="Продавец 💵", callback_data=f"dealer:{call.from_user.id}")
    btn8 = types.InlineKeyboardButton(
        text="Восилий 🤠", callback_data=f"canuman:{call.from_user.id}")
    btn_back = types.InlineKeyboardButton(
        text="⬅️Назад", callback_data=f"main:{call.from_user.id}")
    markup.row(btn1, btn2)
    markup.row(btn3, btn4)
    markup.row(btn5, btn6)
    markup.row(btn7, btn8)
    markup.row(btn_back)
    bot.send_message(call.message.chat.id, "Вы прибыли в город!",
                    reply_markup=markup)

def crossprofile(call):
    if call.from_user.id != int(call.data.split(':')[1]):
        bot.answer_callback_query(callback_query_id=call.id, text="Вы не можете взаимодействовать не со своей кнопкой!")
        return
    if not profile_exists(call.data.split(':')[1]):
        bot.send_message(call.message.chat.id, "Сперва создайте персонажа!")
        return 
    bot.send_message(call.message.chat.id, text="Таинственный Путешественник в разработке..")




def dialogue_hammersmith(call):
    pass



def show_inventory(call):
    if call.from_user.id != int(call.data.split(':')[1]):
        bot.answer_callback_query(callback_query_id=call.id, text="Вы не можете взаимодействовать не со своей кнопкой!")
        return
    if not profile_exists(call.data.split(':')[1]):
        bot.send_message(call.message.chat.id, "Сперва создайте персонажа!")
        return 
    user_id = call.from_user.id
    conn = sqlite3.connect('DunGram.db')
    c = conn.cursor()
    
    # Получаем предметы в инвентаре пользователя (исключая пустые слоты)
    c.execute('''
    SELECT i.ItemName, s.ItemCount
    FROM InventorySlots s
    JOIN Items i ON s.ItemId = i.ItemId
    WHERE s.UserId = ? AND s.ItemCount > 0
    ''', (user_id,))
    inventory_items = c.fetchall()

    # Формируем сообщение с инвентарем
    if inventory_items:
        inventory_message = "🎒 Ваш инвентарь:\n"
        for index, item in enumerate(inventory_items, start=1):
            item_name, item_count = item
            inventory_message += f"     {index}. {item_name}: {item_count} шт.\n"
    else:
        inventory_message = "Ваш инвентарь пуст."

    # Отправляем сообщение с инвентарем пользователю
    bot.send_message(call.message.chat.id, inventory_message)

    conn.close()


# Ты тот самый путешественник? Ну тогда слушай меня внимательно, повторять не люблю, а то были уже такие.
# Справа от тебя находится котел, в который ты будешь закидывать ингридиенты. Выложив определённую комбинцаию ингридиентов ты можешь получить зелье или другой ингридиент
# Известные мне рецепты записаны в книге, которая находится слева от тебя
# Если ты допустил ошибку и закинул лишний ингридиент, то можешь сбросить рецепт забрав все ингридиенты обратно
#
#
#
#
#
#

def show_FAQ(call):
    if call.from_user.id != int(call.data.split(':')[1]):
        bot.answer_callback_query(callback_query_id=call.id, text="Вы не можете взаимодействовать не со своей кнопкой!")
        return
    bot.send_message(call.message.chat.id, "Часто задаваемые вопросы:")


def show_coders(call):
    if call.from_user.id != int(call.data.split(':')[1]):
        bot.answer_callback_query(callback_query_id=call.id, text="Вы не можете взаимодействовать не со своей кнопкой!")
        return
    foo = '''
Разработчик: https://t.me/sanzharirl
Тестеры: @cx10bx, @popaslona210, @HollyNicki, @aquarelka_volodya, 
Копирайтер: @popaslona210
Разработка началась: 04.05.24
Использовано: Python, telebot, SQL

'''
    bot.send_message(call.message.chat.id, text=foo)
