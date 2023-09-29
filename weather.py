
import requests
import datetime

from utils import default_params
from utils import weather_id as _weather_id
from utils import wind as _wind
from utils import clock as _clock
from utils import get_logger

class Forecast:

    def __init__(self) -> None:

        self.r = requests.Session()
        self.logger = get_logger(level='debug')

    def get_weather_12h(self, city) -> dict:
        """
        Метод возвращает ответ API OWM 5d3h погоды
        Документация к api - https://openweathermap.org/forecast5

        :param _type_ city: город для подстановки в запрос. Вернет сообщение если город не найден
        :return dict: 
        """
        url = 'https://api.openweathermap.org/data/2.5/forecast'
        params = default_params
        params['q'] = city
        params['cnt'] = 4
        
        resp = self.r.get(url=url,params=params)

        if resp.status_code != 200:
            self.logger.error(f'{resp.status_code}')
            return 'Проблемы на стороне сервиса. Попробуй попозже'

        return resp.json()

    def get_current_weather(self, city: str) -> dict:
        url = 'https://api.openweathermap.org/data/2.5/weather'
        params = default_params
        params['q'] = city

        resp = self.r.get(url=url, params=params)

        if resp.status_code != 200:
            self.logger.error(f'{resp.status_code}')
            return 'Проблемы на стороне сервиса. Попробуй попозже'

        return resp.json()

    def weather_12h(self, city:str) -> str:
        """
        Метод возвращает распарсеный словарь из get_weather_12h для подстановки в сообщение

        :param str city: город
        :return str: сообщение для передачи боту
        """

        r = self.get_weather_12h(city=city)
        popcount = 0
        l = []
        if r['cod'] == '200':
            for row in r['list']:

                data: datetime.datetime = datetime.datetime.strptime(row['dt_txt'], '%Y-%m-%d %H:%M:%S')
                temp: float = round(row['main']['temp'], 1)
                desc: str = row['weather'][0]['description'].capitalize()
                weather_id: int = row['weather'][0]['id']
                wind: float = round(row["wind"]["speed"], 1)
                pop: float = row['pop']

                popcount += pop
                m = '\n\U0001F6B4\u200D\u2642\uFE0F Можно ехать на велике'

                h = _clock(data.hour)
                warn = _wind(wind)
                wid = _weather_id(weather_id)

                s = f'{h} в {data.hour} {wid} {desc}, {temp} градусов\n{warn} - {wind}\nОсадки - {pop}'
                l.append(s)

                
            if popcount > 1: m = '\n\U0001F327 Возьми дождевик и езжай на метре'
            msg = '\n'.join(l)
            return msg+m
        else: return f'Твой город не найден. /city чтобы добавить свой город'

    def current_weather(self, city):

        r = self.get_current_weather(city=city)

        if isinstance(r, str):
            return r
        
        date = datetime.datetime.fromtimestamp(r['dt'])
        temp = round(r['main']['temp'], 1)
        desc = r['weather'][0]['description'].capitalize()
        weather_id = r['weather'][0]['id']
        sunrise = datetime.datetime.fromtimestamp(r['sys']['sunrise'])
        sunset = datetime.datetime.fromtimestamp(r['sys']['sunset'])
        wind = round(r['wind']['speed'], 1)
        
        fmt='%H:%m'
        
        w = _weather_id(weather_id)
        wi = _wind(wind)
        
        s = f'Погода {date.strftime("%H:%m %d-%m")}\n{w} {desc}, {temp} градусов\nРассвет в {sunrise.strftime(fmt)} Закат в {sunset.strftime(fmt)}\n{wi} {wind} м/с'
        return s
        
        
        

