#!venv/bin/python3

import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

from utils import bot_token
from weather import Forecast
from db import _select, _insert, _update_city

logging.basicConfig(
    format='[%(levelname)s] - %(asctime)s on %(name)s \n --- \n %(message)s',
    level=logging.INFO
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #TODO 1. проверить есть ли id в базе. Если есть то приветствие, если нет, до добавить
    #TODO 2. Клавиатура: Выбрать город, Прогноз
    uid = update.effective_chat.id
    uname = update.effective_chat.username

    name = _select(uid=uid)[0]

    if name == None:
        _insert(user_id=update.effective_chat.id, name=update.effective_chat.username)
        await context.bot.send_message(chat_id=uid, text=f'Приятно познакомиться {uname}. Я погодный бот.\nСкажи мне свой город и я смогу присылать тебе погоду на ближайшее время.\nКоманда /city и твой город')
    
    else: await context.bot.send_message(
        chat_id=uid,
        text=f"С возвращением {uname}, как оно? Не хочешь немного погоды?"
    )

async def city(update: Update, context: ContextTypes.DEFAULT_TYPE):

    city: str = ' '.join(context.args).capitalize()
    uid = update.effective_chat.id

    _update_city(city=city, uid=uid)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'Круто, твой город теперь {city}. Команда /forecast чтобы узнать погоду')

async def forecast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    uid = update.effective_chat.id

    city = _select(uid=uid)[1]

    if city != None:
        w = Forecast()
        w.get_weather(city=city)
        s = w.parse_html()
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=s)

if __name__ == "__main__":

    app = ApplicationBuilder().token(bot_token).build() 

    start_handler = CommandHandler('start', start)
    app.add_handler(start_handler)

    city_handler = CommandHandler('city', city)
    app.add_handler(city_handler)

    forecast_handler = CommandHandler('forecast', forecast)
    app.add_handler(forecast_handler)
    
    app.run_polling()