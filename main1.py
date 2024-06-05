from dotenv import load_dotenv, find_dotenv
import os
from aiogram.filters.command import Command
from aiogram import Bot, Dispatcher, types
import aiogram as gram
import asyncio
import sqlite3
import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger('aiogram')
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)


load_dotenv(find_dotenv())

bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher()

# conn = sqlite3.connect('DunGram.db')
# c = conn.cursor()
# # c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)")
# # c.execute("CREATE TABLE IF NOT EXISTS posts (username TEXT, post TEXT)")
# conn.commit()
# conn.close()

HELP = '''
/help - Список команд,
/description - Описание бота,
/start - Начать игру
'''
DESCRIPTION = '''
Приветствую!
Я - Игровой чат-бот по игре Dungeons, созданный 1 из игроков Cristalix Dungeons.
Coming soon...
'''

kb = types.ReplyKeyboardMarkup(keyboard=[], resize_keyboard=True, one_time_keyboard=True)
kb.keyboard.append([types.KeyboardButton(text="/help")])
kb.keyboard.append([types.KeyboardButton(text="/help")])
kb.keyboard.append([types.KeyboardButton(text="/help")])

inlkb = types.InlineKeyboardMarkup(inline_keyboard=[], row_width=2)
inlkb.inline_keyboard.append([types.InlineKeyboardButton(text="Button 1", url='')])
inlkb.inline_keyboard.append([types.InlineKeyboardButton(text="Button 2", url='')])

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Добро пожаловать в открытое тестирование игры DungeonsRPG!\nПолностью основано на Cristalix Dungeons.",
                        reply_markup=kb)
    await message.delete()


@dp.message(Command('help'))
async def help_command(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                            text=HELP,
                            reply_markup=inlkb
                            )
    await message.delete()


@dp.message(Command('description'))
async def description_command(message: types.Message):
    await message.answer(DESCRIPTION)


async def main():
    await dp.start_polling(bot, allowed_updates=[''])
    print("Bot has started successfully")

if __name__ == "__main__":
    asyncio.run(main())