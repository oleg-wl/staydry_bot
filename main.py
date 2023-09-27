#!venv/bin/python3

import telebot
from telebot import types

from utils import bot_token
from weather import Forecast

bot = telebot.TeleBot(token=bot_token)

@bot.message_handler(commands=['start'])
def send_welcome(message):
	bot.reply_to(message, "Привет. Я отправлю тебе погоду на ближайшие 12 часов.")

@bot.message_handler(commands=['help'])
def send_help(message):
	bot.reply_to(message, 'help')

@bot.message_handler(commands=['прогноз'])
def buttons(message):
    markup = types.ReplyKeyboardMarkup()
    button_msk = types.KeyboardButton('Москва', request_contact=False, request_location=False)
    button_spb = types.KeyboardButton('Санкт-Петербург', request_contact=False, request_location=False)
    markup.row(button_msk,button_spb)
    bot.send_message(message.chat.id, 'Test')

@bot.message_handler(commands=['спб'])
def forecast(message):

    forecast = Forecast()
    forecast.get_weather('Санкт-Петербург')
    msg = forecast.parse_html()

    bot.send_message(message.chat.id, msg, parse_mode='html')

bot.infinity_polling()