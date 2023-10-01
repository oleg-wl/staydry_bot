#!venv/bin/python3
# -*- coding: UTF-8 -*-

#~~~~~~~~~~~~~~~~~~~~~~~
# Основное тело бота
#~~~~~~~~~~~~~~~~~~~~~~~

from telegram import Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

from utils import bot_token, f, decorator_select, city_short_names

import logging

from weather import Forecast
from db import _select, _insert, _update_city

logging.basicConfig(format=f["fmt"], level=logging.DEBUG)

#Логгер для http-запросов
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


buttons = [
    [InlineKeyboardButton("Погода сейчас", callback_data="forecastnow")],
    [InlineKeyboardButton("В ближайщие 12 часов", callback_data="forecast12h")],
]
rep_marcup = InlineKeyboardMarkup(buttons)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_chat.id
    uname = update.effective_chat.username

    name, city = _select(uid=uid)

    if name == None:
        _insert(user_id=update.effective_chat.id, name=update.effective_chat.username)
        await context.bot.send_message(
            chat_id=uid,
            text=f"Приятно познакомиться {uname}. Я погодный бот.\nСкажи мне свой город и я смогу присылать тебе погоду на ближайшее время.\nОтправь мне /city и твой город\nНапример: /city Санкт-Перетбург"
        )
    elif city == None:
        
        await context.bot.send_message(
            chat_id=uid,
            text=f"Привет {uname}. Прости я забыл твой город.\nОтправь мне /city твой город\nНапример: /city Санкт-Перетбург"
        )

    else:
        await context.bot.send_message(
            chat_id=uid,
            text=f"С возвращением {uname}, как оно? Не хочешь немного погоды в городе {city}?",
            reply_markup=rep_marcup
        )

async def help(update, context):
    uid = update.effective_chat.id
    uname = update.effective_chat.username
    url = 'https://github.com/oleg-wl/staydry_bot/issues'
    
    msg = f'Привет {uname},\nБот запомнит твой город и пршлет тебе текущий прогноз и прогноз за ближайшее время\n/start - начни общение с ботом\n/city <i>_твой город_</i> поменять город\n\n&#128204; Если что-то сломалось - пиши мне <a href="{url}">на гитхабе</a>'
    
    await context.bot.send_message(
        chat_id=uid,
        text=msg,
        parse_mode='HTML',
        disable_web_page_preview=True
        )


async def city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city: str = " ".join(context.args).capitalize().strip()
    uid = update.effective_chat.id

    city = city_short_names(city)
    _update_city(city=city, uid=uid)

    if len(city) == 0:
        msg = "Мне нужно знать город. Добавь его к коменде /city\nНапример: /city Новосибирск"
        await context.bot.send_message(chat_id=uid, text=msg)
        return

    msg = f"Круто, твой город {city}"
    await context.bot.send_message(chat_id=uid, text=msg, reply_markup=rep_marcup)


#!Обернуто в декоратор из utils.py
#Декоратор делает запрос в базу данных database.py. 
#Возвращает сообщение с ошибкой (в чат) если в базе нет города или имени пользователя 
@decorator_select(func1=_select)
def forecast_12h(*args, **kwargs):
        return Forecast().weather_12h(*args, **kwargs)

@decorator_select(func1=_select)
def forecast_now(*args, **kwargs):
    return Forecast().current_weather(*args, **kwargs)


async def button(update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_chat.id
    query = update.callback_query
    q = query.data
    await query.answer()

    match q:
        case 'forecastnow':
            m = forecast_now(uid=uid)
        case 'forecast12h':
            m = forecast_12h(uid=uid)

    await query.edit_message_text(text=m, reply_markup=rep_marcup)

async def reply_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    input: str = update.message.text
    uid = update.effective_chat.id

    msg = Forecast().current_weather(city=input.lower().rstrip())

    await update.message.reply_text(text=msg)

    

if __name__ == "__main__":
    app = ApplicationBuilder().token(bot_token).build()

    start_handler = CommandHandler("start", start)
    app.add_handler(start_handler)
    
    help_handler = CommandHandler("help", help)
    app.add_handler(help_handler)

    button_handler = CallbackQueryHandler(button)
    app.add_handler(button_handler)

    city_handler = CommandHandler("city", city)
    app.add_handler(city_handler)

    msg_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, reply_msg)
    app.add_handler(msg_handler)


    app.run_polling()
