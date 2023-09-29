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
        await context.bot.send_message(chat_id=uid, text=f'Приятно познакомиться {uname}. Я погодный бот.\nСкажи мне свой город и я смогу присылать тебе погоду на ближайшее время.\nОтправь мне /city и твой город')
    
    else: await context.bot.send_message(
        chat_id=uid,
        text=f"С возвращением {uname}, как оно? Не хочешь немного погоды?"
    )

async def city(update: Update, context: ContextTypes.DEFAULT_TYPE):

    city: str = ' '.join(context.args).capitalize().strip()
    uid = update.effective_chat.id

    _update_city(city=city, uid=uid)
    msg = f'Круто, твой город теперь {city}. Команда /forecast чтобы узнать погоду'
    if len(city) == 0: msg = 'Мне нужно знать город. Добавь его к коменде /city\nНапример: /city Новосибирск'

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg)

async def forecast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    uid = update.effective_chat.id

    name, city = _select(uid=uid)

    if name == None:
        await context.bot.send_message(chat_id=uid, text='Прости я забыл о нашем знакомтве. Давай начнем с начала. Нажми /start ')
        return

    if (city == None) or (len(city) == 0):
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Прости, я не знаю какой город тебе нужен. Отправь мне /city и название города')
        return

    if city != None:
        w = Forecast()
        w.get_weather(city=city)
        s = w.parse_html()
        
        await context.bot.send_message(
            chat_id=uid,
            text=f'Погода в {city} на ближайшее время\n'+s)

        
if __name__ == "__main__":

    app = ApplicationBuilder().token(bot_token).build() 

    start_handler = CommandHandler('start', start)
    app.add_handler(start_handler)

    city_handler = CommandHandler('city', city)
    app.add_handler(city_handler)

    forecast_handler = CommandHandler('forecast', forecast)
    app.add_handler(forecast_handler)
    
    app.run_polling()