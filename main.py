#!venv/bin/python3
# -*- coding: UTF-8 -*-

from telegram import Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

from utils import bot_token, f

import logging

from weather import Forecast
from db import _select, _insert, _update_city

logging.basicConfig(format=f['fmt'], level=logging.INFO)
logger = logging.getLogger(__name__)


buttons = [
    [InlineKeyboardButton('Погода сейчас' ,callback_data='forecastnow')],
    [InlineKeyboardButton('В ближайщие 12 часов', callback_data='forecast12h')]
    ]
rep_marcup = InlineKeyboardMarkup(buttons)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    if len(city) == 0: 
        msg = 'Мне нужно знать город. Добавь его к коменде /city\nНапример: /city Новосибирск'
        await context.bot.send_message(chat_id=uid, text=msg)
        return
    
    msg = f'Круто, твой город {city}'
    await context.bot.send_message(chat_id=uid, text=msg, reply_markup=rep_marcup)

#!Оберни в декоратор!!!
def forecast_12h(uid):

    name, city = _select(uid=uid)

    if name == None:
        msg = 'Прости я забыл о нашем знакомтве. Давай начнем с начала. Нажми /start '
        return msg

    if (city == None) or (len(city) == 0):
        msg = 'Прости, я не знаю какой город тебе нужен. Отправь мне /city и название города'
        return msg

    if city != None:

        #Получить погоду за 12 часов
        s = Forecast().weather_12h(city=city)
        
        msg = f'Погода в городе {city} на ближайшее время\n\n'+s
        return msg

def forecast_now(uid):
    name, city = _select(uid=uid)

    if name == None:
        msg = 'Прости я забыл о нашем знакомтве. Давай начнем с начала. Нажми /start '
        return msg

    if (city == None) or (len(city) == 0):
        msg = 'Прости, я не знаю какой город тебе нужен. Отправь мне /city и название города'
        return msg

    if city != None:

        #Получить погоду за 12 часов
        s = Forecast().current_weather(city=city)
        
        msg = f'Погода в городе {city}\n'+s
        return msg
    

async def button(update, context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_chat.id
    query = update.callback_query
    q = query.data
    await query.answer()

    if q == 'forecast12h':
        m = forecast_12h(uid=uid)
    elif q == 'forecastnow':
        m = forecast_now(uid=uid)
        
    await query.edit_message_text(text=m, reply_markup=rep_marcup)
        
if __name__ == "__main__":

    app = ApplicationBuilder().token(bot_token).build() 

    start_handler = CommandHandler('start', start)
    app.add_handler(start_handler)

    button_handler = CallbackQueryHandler(button)
    app.add_handler(button_handler)

    city_handler = CommandHandler('city', city)
    app.add_handler(city_handler)

    #forecast_handler = CommandHandler('forecast', forecast)
    #app.add_handler(forecast_handler)
    
    app.run_polling()
