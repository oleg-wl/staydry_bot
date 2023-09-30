
import configparser
import logging
from functools import wraps

from db import select as _select

config = configparser.ConfigParser()
config.read('config.ini')
bot_token = config.get('main', 'botapi')
w_token = config.get('main', 'OWMAPI')

default_params = {
    'appid':w_token,
    'units':'metric',
    'mode':'json',
    'lang':'ru'
    }

f = {
    'fmt':'%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    'datefmt':'%d-%m-%Y, %H:%M:%S'
    }

def get_logger(name:str = __name__, level = 'DEBUG'):
    level = level.upper()
    formatter = logging.Formatter(**f)

    logger = logging.getLogger(name)
    logger.setLevel(level=level)

    ch = logging.StreamHandler()
    ch.setFormatter(formatter)

    logger.addHandler(ch) 
    return logger


# Функции для раскрашивания эмоджими

def weather_id(id: int) -> str:
    """
    Функция возвращает смайлик в зависимости от ID погодных условий

    :param int id: row['weather'][0]['id']
    :return str: смайлик
    """

    if id == 800: #clear sky
        wid = '\uE04A'
    elif id in range(500,532): #rain
        wid = '\U0001F327'
    elif id in range(600, 623): #snow
        wid = '\U0001F328'
    elif id in range(800, 805):
        wid = '\U0001F325'
    else: wid = '\u26C8'
    return wid

def wind(w: float) -> str:
    return '\uE252 Сильный ветер ' if w >= 5 else 'Ветер' 

def clock(h: int) -> str:
    """
    Функция выдает смайлик часов

    :param int h: datetime.datetime.hour или int час
    :return str: смайл часов
    """
    
    if (h == 3) or (h == 15):
        clock = '\uE026' #3
    elif (h == 6) or (h == 18):
        clock = '\U0001F561' # 6 часов
    elif (h == 9) or (h == 21):
        clock = '\uE02C' #9
    elif (h == 12) or (h == 0):
        clock = '\uE02F' # 12
    return clock

#Декораторы 
def decorator(func):
    @wraps(func)
    def wrapper(uid, city):
        
        name, city = _select(uid)

        if name == None:
            msg = "Прости я забыл о нашем знакомтве. Давай начнем с начала. Нажми /start "
            return msg

        if (city == None) or (len(city) == 0):
            msg = "Прости, я не знаю какой город тебе нужен. Отправь мне /city и название города"
            return msg

        if city != None:
        # Получить погоду
            s = wrapper(city=city)
            msg = f"Погода в городе {city} на ближайшее время\n" + s
        return msg
    return func
