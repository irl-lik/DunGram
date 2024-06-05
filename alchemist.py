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


def alchemist(call):
    if call.from_user.id != int(call.data.split(':')[1]):
        bot.answer_callback_query(callback_query_id=call.id, text="Вы не можете взаимодействовать не со своей кнопкой!")
        return
    markup = types.InlineKeyboardMarkup()
    btn_back = types.InlineKeyboardButton(
        text="⬅️Назад", callback_data=f"town:{call.from_user.id}")
    btn1 = types.InlineKeyboardButton(
        text="Алхимик 👨🏽‍⚕️", callback_data=f"dialogue_alchemist:{call.from_user.id}")
    btn2 = types.InlineKeyboardButton(
        text="Варить 🧪", callback_data=f"brew_potions:{call.from_user.id}")
    btn3 = types.InlineKeyboardButton(
        text="Рецепты 📗", callback_data=f"alchemist_recipes:{call.from_user.id}")
    markup.row(btn1, btn2)
    markup.row(btn_back, btn3)
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Вы зашли в зельеварную!",
        reply_markup=markup)

def alchemist_recipes(call):
    if call.from_user.id != int(call.data.split(':')[1]):
        bot.answer_callback_query(callback_query_id=call.id, text="Вы не можете взаимодействовать не со своей кнопкой!")
        return
    markup = types.InlineKeyboardMarkup()
    btn_back = types.InlineKeyboardButton(
        text="⬅️Назад", callback_data=f"alchemist:{call.from_user.id}")
    btn1 = types.InlineKeyboardButton(
        text="Основное 🧩", callback_data=f"standart_crafts:{call.from_user.id}")
    btn3 = types.InlineKeyboardButton(
        text="Лечебное 💊", callback_data=f"heal_crafts:{call.from_user.id}")
    btn4 = types.InlineKeyboardButton(
        text="Вспомогательное ➕", callback_data=f"auxiliary_crafts:{call.from_user.id}")
    btn2 = types.InlineKeyboardButton(
        text="Боевое 🦠", callback_data=f"battle_crafts:{call.from_user.id}")
    markup.row(btn1, btn3)
    markup.row(btn4, btn2)
    markup.row(btn_back)
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Выбери раздел интересующих рецептов: ",
        reply_markup=markup)

def standart_crafts(call):
    if call.from_user.id != int(call.data.split(':')[1]):
        bot.answer_callback_query(callback_query_id=call.id, text="Вы не можете взаимодействовать не со своей кнопкой!")
        return

    conn = sqlite3.connect('DunGram.db')
    c = conn.cursor()
    c.execute("SELECT ResultItemID, Ingredients FROM Recipes WHERE RecipeClass = 1")
    recipes = c.fetchall()
    if recipes:
        recipe_message = "Базовые Рецепты:\n"
        for result_item_id, ingredient_list_str in recipes:
            ingredient_list = json.loads(ingredient_list_str)
            ingredient_names = [f"{get_item_name(ingredient[0])} ({ingredient[1]} шт.)" for ingredient in ingredient_list]
            ingredient_str = ", ".join(ingredient_names)
            recipe_message += f"Результат: {get_item_name(result_item_id)}\nИнгредиенты: {ingredient_str}\n\n"
    else:
        recipe_message = "Пока нет доступных рецептов."
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="⬅️Назад", callback_data=f"alchemist_recipes:{call.from_user.id}")
    markup.row(btn1)

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=recipe_message,
        reply_markup=markup)

    conn.close()

def heal_crafts(call):
    if call.from_user.id != int(call.data.split(':')[1]):
        bot.answer_callback_query(callback_query_id=call.id, text="Вы не можете взаимодействовать не со своей кнопкой!")
        return

    conn = sqlite3.connect('DunGram.db')
    c = conn.cursor()
    c.execute("SELECT ResultItemID, Ingredients FROM Recipes WHERE RecipeClass = 2")
    recipes = c.fetchall()
    if recipes:
        recipe_message = "Лечебные Рецепты:\n"
        for result_item_id, ingredient_list_str in recipes:
            ingredient_list = json.loads(ingredient_list_str)
            ingredient_names = [f"{get_item_name(ingredient[0])} ({ingredient[1]} шт.)" for ingredient in ingredient_list]
            ingredient_str = ", ".join(ingredient_names)
            recipe_message += f"Результат: {get_item_name(result_item_id)}\nИнгредиенты: {ingredient_str}\n\n"
    else:
        recipe_message = "Пока нет доступных рецептов."
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="⬅️Назад", callback_data=f"alchemist_recipes:{call.from_user.id}")
    markup.row(btn1)

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=recipe_message,
        reply_markup=markup)

    conn.close()

def auxiliary_crafts(call):
    if call.from_user.id != int(call.data.split(':')[1]):
        bot.answer_callback_query(callback_query_id=call.id, text="Вы не можете взаимодействовать не со своей кнопкой!")
        return

    conn = sqlite3.connect('DunGram.db')
    c = conn.cursor()
    c.execute("SELECT ResultItemID, Ingredients FROM Recipes WHERE RecipeClass = 3")
    recipes = c.fetchall()
    if recipes:
        recipe_message = "Лечебные Рецепты:\n"
        for result_item_id, ingredient_list_str in recipes:
            ingredient_list = json.loads(ingredient_list_str)
            ingredient_names = [f"{get_item_name(ingredient[0])} ({ingredient[1]} шт.)" for ingredient in ingredient_list]
            ingredient_str = ", ".join(ingredient_names)
            recipe_message += f"Результат: {get_item_name(result_item_id)}\nИнгредиенты: {ingredient_str}\n\n"
    else:
        recipe_message = "Пока нет доступных рецептов."
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="⬅️Назад", callback_data=f"alchemist_recipes:{call.from_user.id}")
    markup.row(btn1)

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=recipe_message,
        reply_markup=markup)

    conn.close()

def battle_crafts(call):
    if call.from_user.id != int(call.data.split(':')[1]):
        bot.answer_callback_query(callback_query_id=call.id, text="Вы не можете взаимодействовать не со своей кнопкой!")
        return

    conn = sqlite3.connect('DunGram.db')
    c = conn.cursor()
    c.execute("SELECT ResultItemID, Ingredients FROM Recipes WHERE RecipeClass = 4")
    recipes = c.fetchall()
    if recipes:
        recipe_message = "Лечебные Рецепты:\n"
        for result_item_id, ingredient_list_str in recipes:
            ingredient_list = json.loads(ingredient_list_str)
            ingredient_names = [f"{get_item_name(ingredient[0])} ({ingredient[1]} шт.)" for ingredient in ingredient_list]
            ingredient_str = ", ".join(ingredient_names)
            recipe_message += f"Результат: {get_item_name(result_item_id)}\nИнгредиенты: {ingredient_str}\n\n"
    else:
        recipe_message = "Пока нет доступных рецептов."
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="⬅️Назад", callback_data=f"alchemist_recipes:{call.from_user.id}")
    markup.row(btn1)

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=recipe_message,
        reply_markup=markup)

    conn.close()


def brew_potions(call):
    if call.from_user.id != int(call.data.split(':')[1]):
        bot.answer_callback_query(callback_query_id=call.id, text="Вы не можете взаимодействовать не со своей кнопкой!")
        return
    markup = types.InlineKeyboardMarkup()
    btn_back = types.InlineKeyboardButton(
        text="⬅️Назад", callback_data=f"alchemist:{call.from_user.id}")
    btn1 = types.InlineKeyboardButton(
        text="Основное 🧩", callback_data=f"brew_basic:{call.from_user.id}")
    btn3 = types.InlineKeyboardButton(
        text="Лечебное 💊", callback_data=f"brew_heal:{call.from_user.id}")
    btn4 = types.InlineKeyboardButton(
        text="Вспомогательное ➕", callback_data=f"brew_auxiliary:{call.from_user.id}")
    btn2 = types.InlineKeyboardButton(
        text="Боевое 🦠", callback_data=f"brew_battle:{call.from_user.id}")
    markup.row(btn1, btn3)
    markup.row(btn4, btn2)
    markup.row(btn_back)
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Выбери раздел интересующих рецептов: ",
        reply_markup=markup)

def brew_basic(call):
    if call.from_user.id != int(call.data.split(':')[1]):
        bot.answer_callback_query(callback_query_id=call.id, text="Вы не можете взаимодействовать не со своей кнопкой!")
        return
    conn = sqlite3.connect('DunGram.db')
    c = conn.cursor()
    c.execute("SELECT ResultItemID, Ingredients FROM Recipes WHERE RecipeClass = 1")
    recipes = c.fetchall()
    if recipes:
        # Создание кнопок с результатами и текста сообщения
        markup = types.InlineKeyboardMarkup()
        recipe_message = "Выберите рецепт для приготовления:\n\n"
        for idx, (result_item_id, ingredient_list_str) in enumerate(recipes, start=1):
            ingredient_list = json.loads(ingredient_list_str)
            ingredient_names = [f"{get_item_name(ingredient[0])} ({ingredient[1]} шт.)" for ingredient in ingredient_list]
            ingredient_str = ", ".join(ingredient_names)
            result_item_name = get_item_name(result_item_id)
            recipe_button = types.InlineKeyboardButton(text=f"{result_item_name}", callback_data=f"brew_step_1:{call.from_user.id}:{result_item_id}")
            markup.add(recipe_button)
            recipe_message += f"{idx}. {result_item_name}: \n{ingredient_str}\n\n"
        btn_back = types.InlineKeyboardButton(text="⬅️Назад", callback_data=f"brew_potions:{call.from_user.id}")
        markup.row(btn_back)

        # Отправка сообщения с рецептами и кнопками
        bot.send_message(chat_id=call.message.chat.id, text=recipe_message, reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id, "Пока нет доступных рецептов.")
    conn.close()

def brew_heal(call):
    if call.from_user.id != int(call.data.split(':')[1]):
        bot.answer_callback_query(callback_query_id=call.id, text="Вы не можете взаимодействовать не со своей кнопкой!")
        return
    conn = sqlite3.connect('DunGram.db')
    c = conn.cursor()
    c.execute("SELECT ResultItemID, Ingredients FROM Recipes WHERE RecipeClass = 2")
    recipes = c.fetchall()
    if recipes:
        # Создание кнопок с результатами и текста сообщения
        markup = types.InlineKeyboardMarkup()
        recipe_message = "Выберите рецепт для приготовления:\n\n"
        for idx, (result_item_id, ingredient_list_str) in enumerate(recipes, start=1):
            ingredient_list = json.loads(ingredient_list_str)
            ingredient_names = [f"{get_item_name(ingredient[0])} ({ingredient[1]} шт.)" for ingredient in ingredient_list]
            ingredient_str = ", ".join(ingredient_names)
            result_item_name = get_item_name(result_item_id)
            recipe_button = types.InlineKeyboardButton(text=f"{result_item_name}", callback_data=f"brew_step_1:{call.from_user.id}:{result_item_id}")
            markup.add(recipe_button)
            recipe_message += f"{idx}. {result_item_name}: \n{ingredient_str}\n\n"
        btn_back = types.InlineKeyboardButton(text="⬅️Назад", callback_data=f"brew_potions:{call.from_user.id}")
        markup.row(btn_back)

        # Отправка сообщения с рецептами и кнопками
        bot.send_message(chat_id=call.message.chat.id, text=recipe_message, reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id, "Пока нет доступных рецептов.")
    conn.close()

def brew_auxiliary(call):
    if call.from_user.id != int(call.data.split(':')[1]):
        bot.answer_callback_query(callback_query_id=call.id, text="Вы не можете взаимодействовать не со своей кнопкой!")
        return
    conn = sqlite3.connect('DunGram.db')
    c = conn.cursor()
    c.execute("SELECT ResultItemID, Ingredients FROM Recipes WHERE RecipeClass = 3")
    recipes = c.fetchall()
    if recipes:
        # Создание кнопок с результатами и текста сообщения
        markup = types.InlineKeyboardMarkup()
        recipe_message = "Выберите рецепт для приготовления:\n\n"
        for idx, (result_item_id, ingredient_list_str) in enumerate(recipes, start=1):
            ingredient_list = json.loads(ingredient_list_str)
            ingredient_names = [f"{get_item_name(ingredient[0])} ({ingredient[1]} шт.)" for ingredient in ingredient_list]
            ingredient_str = ", ".join(ingredient_names)
            result_item_name = get_item_name(result_item_id)
            recipe_button = types.InlineKeyboardButton(text=f"{result_item_name}", callback_data=f"brew_step_1:{call.from_user.id}:{result_item_id}")
            markup.add(recipe_button)
            recipe_message += f"{idx}. {result_item_name}: \n{ingredient_str}\n\n"
        btn_back = types.InlineKeyboardButton(text="⬅️Назад", callback_data=f"brew_potions:{call.from_user.id}")
        markup.row(btn_back)

        # Отправка сообщения с рецептами и кнопками
        bot.send_message(chat_id=call.message.chat.id, text=recipe_message, reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id, "Пока нет доступных рецептов.")
    conn.close()

def brew_battle(call):
    if call.from_user.id != int(call.data.split(':')[1]):
        bot.answer_callback_query(callback_query_id=call.id, text="Вы не можете взаимодействовать не со своей кнопкой!")
        return
    conn = sqlite3.connect('DunGram.db')
    c = conn.cursor()
    c.execute("SELECT ResultItemID, Ingredients FROM Recipes WHERE RecipeClass = 3")
    recipes = c.fetchall()
    if recipes:
        # Создание кнопок с результатами и текста сообщения
        markup = types.InlineKeyboardMarkup()
        recipe_message = "Выберите рецепт для приготовления:\n\n"
        for idx, (result_item_id, ingredient_list_str) in enumerate(recipes, start=1):
            ingredient_list = json.loads(ingredient_list_str)
            ingredient_names = [f"{get_item_name(ingredient[0])} ({ingredient[1]} шт.)" for ingredient in ingredient_list]
            ingredient_str = ", ".join(ingredient_names)
            result_item_name = get_item_name(result_item_id)
            recipe_button = types.InlineKeyboardButton(text=f"{result_item_name}", callback_data=f"brew_step_1:{call.from_user.id}:{result_item_id}")
            markup.add(recipe_button)
            recipe_message += f"{idx}. {result_item_name}: \n{ingredient_str}\n\n"
        btn_back = types.InlineKeyboardButton(text="⬅️Назад", callback_data=f"brew_potions:{call.from_user.id}")
        markup.row(btn_back)

        # Отправка сообщения с рецептами и кнопками
        bot.send_message(chat_id=call.message.chat.id, text=recipe_message, reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id, "Пока нет доступных рецептов.")
    conn.close()


def brew_step_1(call):
    if call.from_user.id != int(call.data.split(':')[1]):
        bot.answer_callback_query(callback_query_id=call.id, text="Вы не можете взаимодействовать не со своей кнопкой!")
        return
    conn = sqlite3.connect('DunGram.db')
    c = conn.cursor()
    c.execute("SELECT Ingredients FROM Recipes WHERE ResultItemID=?", (call.data.split(':')[2],))
    ingredients = c.fetchone()
    if check_inventory(call.from_user.id, ingredients[0]):
        for item_id, item_count in json.loads(ingredients[0]):
            bot.send_message(call.message.chat.id, f"Вы разложили {get_item_name(item_id)} ({item_count} шт.) возле котла 🧮")
        markup = types.InlineKeyboardMarkup()
        result_item_id = call.data.split(':')[2]
        btn1 = types.InlineKeyboardButton(text="Закинуть 🥘", callback_data=f"brew_step_2:{call.from_user.id}:{result_item_id}:{ingredients}")
        markup.row(btn1)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Вы разложили нужные ингредиенты возле котла, закиньте их туда!",
            reply_markup=markup
            )
    else:
        bot.send_message(call.message.chat.id, text="В Вашем инвентаре недостаточно ингредиентов!")
    conn.commit()
    conn.close()

def brew_step_2(call):
    if call.from_user.id != int(call.data.split(':')[1]):
        bot.answer_callback_query(callback_query_id=call.id, text="Вы не можете взаимодействовать не со своей кнопкой!")
        return
    ingredients = call.data.split(':')[3]
    user_id = call.data.split(':')[1]
    brew_script = ''
    for item_id, item_count in json.loads(ingredients[2:-3]):
        brew_script += f'UPDATE InventorySlots SET ItemCount = ItemCount - {item_count} WHERE UserId = {user_id} AND ItemId = {item_id}; '
        bot.send_message(call.message.chat.id, f"Вы закинули {get_item_name(item_id)} ({item_count} шт.) в котёл 🔥")
    
    conn = sqlite3.connect('DunGram.db')
    c = conn.cursor()
    c.executescript(brew_script)
    conn.commit()
    conn.close()

    markup = types.InlineKeyboardMarkup()
    result_item_id = call.data.split(':')[2]
    btn1 = types.InlineKeyboardButton(text="Перемешать 🥄", callback_data=f"brew_step_3:{call.from_user.id}:{result_item_id}:{call.data.split(':')[3]}")
    markup.row(btn1)
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Вы закинули нужные ингредиенты в котёл, перемешайте их!",
        reply_markup=markup
    )

def brew_step_3(call):
    if call.from_user.id != int(call.data.split(':')[1]):
        bot.answer_callback_query(callback_query_id=call.id, text="Вы не можете взаимодействовать не со своей кнопкой!")
        return
    result_item_id = call.data.split(':')[2]
    ingredients = call.data.split(':')[3]
    if check_inventory(call.from_user.id, ingredients[2:-3]):
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(text="Забрать 🌀", callback_data=f"brew_step_4:{call.from_user.id}:{result_item_id}")
        markup.row(btn1)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Вы закончили варку, заберите результат!",
            reply_markup=markup
        )
    else:
        bot.send_message(call.message.chat.id, text="Вселенная отторгла Вас, Вы пытались обмануть её...")

def brew_step_4(call) -> None:
    if call.from_user.id != int(call.data.split(':')[1]):
        bot.answer_callback_query(callback_query_id=call.id, text="Вы не можете взаимодействовать не со своей кнопкой!")
        return
    user_id = call.data.split(':')[1]
    result_item_id = call.data.split(':')[2]
    conn = sqlite3.connect('DunGram.db')
    c = conn.cursor()
    c.execute("SELECT ResultItemCount FROM Recipes WHERE ResultItemID=?", (result_item_id,))
    result_count = c.fetchone()
    brew_script = add_item_to_inventory(user_id, result_item_id, result_count[0])
    if (int(result_item_id) in [21, 22, 23, 24]) and brew_script is False:
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(
            text="Погрустить ☹️",
            callback_data="a"
        )
        markup.row(btn1)
        bot.edit_message_text(chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            text="Вселенная отторгла Вас, Вы пытались обмануть её...\nОграничение в зельях лечения - 20шт.\nИнгредиенты утеряны",
                            reply_markup=markup)
        return
    c.execute(brew_script)
    conn.commit()
    conn.close()
    markup = types.InlineKeyboardMarkup()
    btn_back = types.InlineKeyboardButton(text="⬅️Назад", callback_data=f"alchemist:{call.from_user.id}")
    markup.row(btn_back)
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Вы забрали {get_item_name(result_item_id)} ({result_count[0]} шт.)",
        reply_markup=markup
    )


def dialogue_alchemist(call):
    if call.from_user.id != int(call.data.split(':')[1]):
        bot.answer_callback_query(callback_query_id=call.id, text="Вы не можете взаимодействовать не со своей кнопкой!")
        return
    foo = ("〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️\nМедленно вступай в мою зельеварню, герой.  Я – тот, кто владеет древними тайнами, чьи зелья сотканы из  магии и многолетнего опыта. Здесь тянется запах таинственных ингредиентов, вибрирует воздух загадок и заговоренных слов.♨️\n"
        "Слушай меня внимательно, повторять не люблю, а то были уже такие.\n"
        "Справа от тебя стоит котёл, закидывай в него  ингредиенты, следуй рецептам в моей книге, и ты сотворишь зелье или другой ингредиент. И помни, не утащи с собою больше 20 флаконов лечебных зелий – таково мое правило!⚠️\n"
        "Также будь готов к испытаниям! Я могу давать тебе задания, выполнишь для меня парочку может и открою тебе секреты алхимии. А теперь ступай, если не собираешься ничего создавать!🌀\n"
        "〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️")
    bot.send_message(call.message.chat.id, foo)