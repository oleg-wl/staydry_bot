#!venv/bin/python3
# -*- coding: UTF-8 -*-

from telegram import Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
)

from utils import bot_token, f, decorator_select

import logging

from weather import Forecast
from db import _select, _insert, _update_city

logging.basicConfig(format=f["fmt"], level=logging.DEBUG)
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
            text=f"Привет {uname}. Прости я забыл твой город погодный бот.\nОтправь мне /city твой город\nНапример: /city Санкт-Перетбург"
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

    # Сокращения городов
    match city.lower():
        case "питер" | "спб" | "болото" | 'санктпетербург' | 'санктпитербург':
            city = "Санкт-Петербург"
        case 'мск' | 'масква':
            city = 'Москва'

        case _:
            pass 
        
    _update_city(city=city, uid=uid)

    if len(city) == 0:
        msg = "Мне нужно знать город. Добавь его к коменде /city\nНапример: /city Новосибирск"
        await context.bot.send_message(chat_id=uid, text=msg)
        return

    msg = f"Круто, твой город {city}"
    await context.bot.send_message(chat_id=uid, text=msg, reply_markup=rep_marcup)


#!Обернуто в декоратор из utils.py
#Декоратор делает запрос в базу. 
#Проверка что name и city есть в database.db
#Если имя и город есть, делается запрос к Апи. 
#Если ошибка (задекорирована) возвращает сообщение об ошибке
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

    #await context.bot.send_message(chat_id=uid, text=m, reply_markup=rep_marcup)
    await query.edit_message_text(text=m, reply_markup=rep_marcup)


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

    # forecast_handler = CommandHandler('forecast', forecast)
    # app.add_handler(forecast_handler)

    app.run_polling()
