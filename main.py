import telebot
from telebot import types
import sqlite3

import logging
from dotenv import load_dotenv, find_dotenv
import os
import time
from components import *
import callbacks
import alchemist
import dealer
import canuman
import sortie

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('telebot')
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

load_dotenv(find_dotenv())
bot = telebot.TeleBot(os.getenv('TOKEN'))
start_time = time.time()
@bot.message_handler(func=lambda message: message.date < start_time)
def handle_old_updates(message):
    pass

@bot.message_handler(func=lambda message: 'стычка' in message.text)
def messages_sort(message):
    if message.text == 'стычка атака':
        sortie.attack(message)
    elif message.text in ['стычка прервать', 'стычка сбежать']:
        sortie.sortie_end(message)

START = 'Добро пожаловать на закрытое тестирование игры DungeonsRPG!\nПолностью основано на Cristalix Dungeons.'

@bot.message_handler(commands = ['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    btn_start = types.InlineKeyboardButton(text='Начать игру ⚔️', callback_data=f'start_game:{message.from_user.id}')
    btn1 = types.InlineKeyboardButton(text='Персонаж 🐾', callback_data=f'character:{message.from_user.id}')
    btn2 = types.InlineKeyboardButton(text='Город 🏰', callback_data=f'town:{message.from_user.id}')
    btn3 = types.InlineKeyboardButton(text='Инвентарь 🎒', callback_data=f'inventory:{message.from_user.id}')
    btn4 = types.InlineKeyboardButton(text='FAQ ❓', callback_data=f'FAQ:{message.from_user.id}')
    btn_code = types.InlineKeyboardButton(text='О разработчиках 👨🏻‍💻', callback_data=f'coders:{message.from_user.id}')
    markup.add(btn_start)
    markup.row(btn1, btn2)
    markup.row(btn3, btn4)
    markup.add(btn_code)
    bot.send_message(message.chat.id, START,
                            reply_markup = markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('main'))
def handle_main_callback(call):
    user_id = call.from_user.id
    if not profile_exists(user_id):
        bot.send_message(call.chat.id, "Сперва создайте персонажа!")
        return 
    markup = types.InlineKeyboardMarkup()
    btn_start = types.InlineKeyboardButton(text='Начать игру ⚔️', callback_data=f'start_game:{call.from_user.id}')
    btn1 = types.InlineKeyboardButton(text='Персонаж 🐾', callback_data=f'character:{call.from_user.id}')
    btn2 = types.InlineKeyboardButton(text='Город 🏰', callback_data=f'town:{call.from_user.id}')
    btn3 = types.InlineKeyboardButton(text='Инвентарь 🎒', callback_data=f'inventory:{call.from_user.id}')
    btn4 = types.InlineKeyboardButton(text='FAQ ❓', callback_data=f'FAQ:{call.from_user.id}')
    btn_code = types.InlineKeyboardButton(text='О разработчиках 👨🏻‍💻', callback_data=f'coders:{call.from_user.id}')
    markup.add(btn_start)
    markup.row(btn1, btn2)
    markup.row(btn3, btn4)
    markup.add(btn_code)
    bot.send_message(call.message.chat.id, text="Dungeons нуждается в тебе..",
                            reply_markup = markup)

@bot.message_handler(commands = ['inventory'])
def handle_inventory(message):
    user_id = message.from_user.id
    if not profile_exists(user_id):
        bot.send_message(message.chat.id, "Сперва создайте персонажа!")
        return 
    conn = sqlite3.connect('DunGram.db')
    c = conn.cursor()

    # Получаем предметы в инвентаре пользователя
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
        for index, (item_name, item_count) in enumerate(inventory_items, start=1):
            inventory_message += f"     {index}. {item_name}: {item_count} шт.\n"
    else:
        inventory_message = "Ваш инвентарь пуст."

    # Отправляем сообщение с инвентарем пользователю
    bot.send_message(message.chat.id, inventory_message)

    conn.close()

@bot.message_handler(commands=['town'])
def town(message):
    user_id = message.from_user.id
    if not profile_exists(user_id):
        bot.send_message(message.chat.id, "Сперва создайте персонажа!")
        return 
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(
        text="Топ 🏆", callback_data=f"top:{message.from_user.id}")
    btn2 = types.InlineKeyboardButton(
        text="Подземелья 🪬", callback_data=f"enter_dungeon:{message.from_user.id}")
    btn3 = types.InlineKeyboardButton(
        text="Хранилище 📦", callback_data=f"storage:{message.from_user.id}")
    btn4 = types.InlineKeyboardButton(
        text="Путешественник 🤔", callback_data=f"crossprofile:{message.from_user.id}")
    btn5 = types.InlineKeyboardButton(
        text="Кузнец 🔨", callback_data=f"hammersmith:{message.from_user.id}")
    btn6 = types.InlineKeyboardButton(
        text="Алхимик 🧪", callback_data=f"alchemist:{message.from_user.id}")
    btn7 = types.InlineKeyboardButton(
        text="Продавец 💵", callback_data=f"dealer:{message.from_user.id}")
    btn8 = types.InlineKeyboardButton(
        text="Восилий 🤠", callback_data=f"canuman:{message.from_user.id}")
    btn_back = types.InlineKeyboardButton(
        text="⬅️Назад", callback_data=f"main:{message.from_user.id}")
    markup.row(btn1, btn2)
    markup.row(btn3, btn4)
    markup.row(btn5, btn6)
    markup.row(btn7, btn8)
    markup.row(btn_back)
    bot.send_message(message.chat.id, "Вы прибыли в город!",
                    reply_markup=markup)

@bot.message_handler(commands=['character'])
def character(message):
    user_id = message.from_user.id
    if not profile_exists(user_id):
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(
            text="Воин 🛡", callback_data=f"select_warrior:{message.from_user.id}")
        btn2 = types.InlineKeyboardButton(
            text="Маг 🧙‍♂️", callback_data=f"select_wiz:{message.from_user.id}")
        btn3 = types.InlineKeyboardButton(
            text="Ассасин 🥷", callback_data=f"select_assasin:{message.from_user.id}")
        btn4 = types.InlineKeyboardButton(
            text="О классах 👑", callback_data=f"about_classes:{message.from_user.id}")
        markup.row(btn1, btn2, btn3)
        markup.row(btn4)
        bot.send_message(message.chat.id, "У Вас пока нет персонажа!\nВыберите класс:",
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
        message_text = (
            f"Вас зовут: {user[1]}🔅\n"
            f"Ваш класс: {profile[2]}{class_emoji}\n"
            f"Уровень: {profile[3]}🆙\n"
            f"Опыт: {profile[4]}⚜️\n"
            f"Количество изумрудов: {balance}💎\n\n"
            f"Зарегистрирован: {user[2]}🕓"
        )
        bot.send_message(message.chat.id,
                        text=message_text,
                        reply_markup=markup,
                        )


@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    callbacks_dict = {
        'start_game': callbacks.start_game,
        'character': callbacks.character,
        'town': callbacks.town,
        'inventory': callbacks.show_inventory,
        'FAQ': callbacks.show_FAQ,
        'coders': callbacks.show_coders,
        'about_classes': callbacks.about_classes,
        'select_warrior': callbacks.select_warrior,
        'select_wiz': callbacks.select_wiz,
        'select_assasin': callbacks.select_assasin,
        'crossprofile': callbacks.crossprofile,
        'alchemist': alchemist.alchemist,
        'dialogue_alchemist': alchemist.dialogue_alchemist,
        'alchemist_recipes': alchemist.alchemist_recipes,
        'standart_crafts': alchemist.standart_crafts,
        'heal_crafts': alchemist.heal_crafts,
        'auxiliary_crafts': alchemist.auxiliary_crafts,
        'battle_crafts': alchemist.battle_crafts,
        'brew_potions': alchemist.brew_potions,
        'brew_basic': alchemist.brew_basic,
        'brew_heal': alchemist.brew_heal,
        'brew_auxiliary': alchemist.brew_auxiliary,
        'brew_battle': alchemist.brew_battle,
        'brew_step_1': alchemist.brew_step_1,
        'brew_step_2': alchemist.brew_step_2,
        'brew_step_3': alchemist.brew_step_3,
        'brew_step_4': alchemist.brew_step_4,
        'dealer': dealer.dealer,
        'dealer_sell': dealer.dealer_sell,
        'canuman': canuman.canuman,
        'canuman_quest': canuman.canuman_quest,
        'sortie': sortie.sortie,
        'sortie_streets': sortie.sortie_streets,
        'sortie_advance_streets': sortie.sortie_advance_streets,
        'sortie_continue': sortie.sortie_continue,
    }
    
    callback_function = callbacks_dict.get(call.data.split(':')[0])
    if callback_function:
        callback_function(call)


@bot.message_handler(commands = ['main'])
def main(message):
    user_id = message.from_user.id
    if not profile_exists(user_id):
        bot.send_message(message.chat.id, "Сперва создайте персонажа!")
        return 
    markup = types.InlineKeyboardMarkup()
    btn_start = types.InlineKeyboardButton(text='Начать игру ⚔️', callback_data=f'start_game:{message.from_user.id}')
    btn1 = types.InlineKeyboardButton(text='Персонаж 🐾', callback_data=f'character:{message.from_user.id}')
    btn2 = types.InlineKeyboardButton(text='Город 🏰', callback_data=f'town:{message.from_user.id}')
    btn3 = types.InlineKeyboardButton(text='Инвентарь 🎒', callback_data=f'inventory:{message.from_user.id}')
    btn4 = types.InlineKeyboardButton(text='FAQ ❓', callback_data=f'FAQ:{message.from_user.id}')
    btn_code = types.InlineKeyboardButton(text='О разработчиках 👨🏻‍💻', callback_data=f'coders:{message.from_user.id}')
    markup.add(btn_start)
    markup.row(btn1, btn2)
    markup.row(btn3, btn4)
    markup.add(btn_code)
    bot.send_message(message.chat.id, text="Dungeons нуждается в тебе..",
                            reply_markup = markup)
bot.polling(none_stop=True, interval=0, skip_pending=True)
bot.stop_polling()