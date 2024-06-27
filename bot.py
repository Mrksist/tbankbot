import asyncio
import telebot
from aiogram import Bot, types, Dispatcher
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.input_file import FSInputFile
import sqlite3

from db import add_budget, set_budget, get_budget, get_report, add_income
from bottoken import TOKEN

connection = sqlite3.connect("a.db")
cursor = connection.cursor()

cursor.execute('''
        CREATE TABLE IF NOT EXISTS  users (
            ID varchar(11),
            BALANCE bigint
        )         
        ''')
cursor.execute('''
        CREATE TABlE If NoT EXISTS HISTORY (
            ID varchar(11),
            VAL bigint,
            DESCRIPTION text,
            CDATE datetime
        )
''')


bot = Bot(token=TOKEN) 
dp = Dispatcher()

async def main():
    await dp.start_polling(bot)

@dp.message(Command('start'))
async def start_command(message : types.Message):
    res = add_budget(cursor,message.from_user.id)
    if res == "EXISTS":
        await message.answer("Приветствуем вас снова. Получить список всех команд: /help")
    elif res == "SUCCESS":
        await message.answer("Приветствуем вас. Ваш стартовый бюджет: 0. Вы можете установить его с помощью /setbudget. Все команды: /help")


@dp.message(Command("help"))
async def process_start_command(message: types.Message):
    await message.answer(''' Вот все доступные команды бота:
/addincome - Добавление дохода\n
/addexpense - Добавление расхода\n
/setbudget - Установка бюджета\n
/budget - Проверка текущего состояния бюджета\n
/report - Получение отчета о доходах и расходах
    ''')
@dp.message(Command("addincome"))
async def cmd_addincome(message: types.Message):
    args = message.text.split(" ")
    if len(args) < 3:
        await message.answer("Используйте <code>/addincome &lt;value&gt; &lt;description&gt;</code>, где <code>&lt;value&gt;</code> - размер дохода, <code>&lt;description&gt;</code> - описание расхода",parse_mode=ParseMode.HTML)
        return 0
    add_income(cursor,message.from_user.id,int(args[1]),args[2])
    connection.commit()
    await message.answer("Доход успешно добавлен")
    

@dp.message(Command("addexpense"))
async def cmd_addexpense(message: types.Message):
    args = message.text.split(" ")
    if len(args) < 3:
        await message.answer("Используйте <code>/addexpense &lt;value&gt; &lt;description&gt;</code>, где <code>&lt;value&gt;</code> - размер расхода, <code>&lt;description&gt;</code> - описание расхода",parse_mode=ParseMode.HTML)
        return 0
    res = add_income(cursor,message.from_user.id,-int(args[1]),args[2])
    connection.commit()
    if res == 'ERR_BUDGET_TOO_LOW':
        await message.answer("Ваш бюджет слишком мал для заявленного дохода")
        return 0
    await message.answer("Расход успешно добавлен")


@dp.message(Command("setbudget"))
async def cmdbalance(message: types.Message):
    mes = message.text.split(" ")
    if(len(mes) < 2):
        await message.answer("Используйте <code>/setbudget &lt;budget&gt;</code>, где <code>&lt;budget&gt;</code> - ваш бюджет",parse_mode=ParseMode.HTML)
        return 0
    x = set_budget(cursor,message.from_user.id,message.text.split(" ")[1])
    connection.commit()
    if x == 'ERR_USR_NOT_FOUND':
        await message.answer("Пользователь не найден")
    else:
        await message.answer("Вы установили бюджет")


@dp.message(Command("budget"))
async def cmd_balance(message: types.Message):
    x = get_budget(cursor,message.from_user.id)
    if x == 'ERR_USR_NOT_FOUND':
        await message.answer("Пользователь не найден")
    else:
        await message.answer(f"Ваш бюджет: {x}")

@dp.message(Command("report"))
async def cmd_report(message: types.Message):
    x = get_report(cursor,message.from_user.id)
    if len(x) != 2:
        await message.answer(x)
    else:
        path = x[1]
        content = x[0]
        photo = FSInputFile(path)
        await bot.send_photo(message.chat.id,photo=photo,caption=content)
        try:
            os.remove(path)
        except:
            pass

if __name__ == "__main__":
    asyncio.run(main())
