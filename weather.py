import requests
import datetime

from utils import default_params
from utils import weather_id as _weather_id
from utils import wind as _wind
from utils import clock as _clock
from utils import city_short_names as _city_short_names

class Forecast:

    def __init__(self) -> None:

        self.r = requests.Session()

    def tzoffset(self, utc: int, timezone:int) -> datetime.datetime:
        utc_time = datetime.datetime.fromtimestamp(utc, tz=datetime.timezone.utc)
        offset = datetime.timedelta(seconds=timezone)
        
        dt =  utc_time + offset
        return dt

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

        return resp.json()

    def get_current_weather(self, city: str) -> dict:
        url = 'https://api.openweathermap.org/data/2.5/weather'
        params = default_params
        params['q'] = city

        resp = self.r.get(url=url, params=params)

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
            tz = r['city']['timezone']

            for row in r['list']:
                d = row['dt']
                    
                data = self.tzoffset(d, tz)
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

                s = f'{h} в {data.hour} {wid}\n{desc}, {temp} градусов\n{warn} - {wind}\nОсадки - {pop}'
                l.append(s)

                
            if popcount > 1: m = '\n\U0001F327 Возьми дождевик и езжай на метре'
            msg = '\n'.join(l)
            return msg+m
        else: return 'Твой город не найден'

    def current_weather(self, city):

        city = _city_short_names(city)
        r = self.get_current_weather(city=city)

        if r['cod'] == 200:
            tz = r['timezone']
            dt  = r['dt']
            date = self.tzoffset(dt, tz)

            temp = round(r['main']['temp'], 1)
            desc = r['weather'][0]['description'].capitalize()
            weather_id = r['weather'][0]['id']
            sunrise = self.tzoffset(r['sys']['sunrise'], tz)
            sunset = self.tzoffset(r['sys']['sunset'], tz)
            wind = round(r['wind']['speed'], 1)
            rain = r.get('rain')
            snow = r.get('snow')
            name = r['name']

            if rain != None:
                warn = '\n\U0001F327 Идет дождик'
            elif snow != None: warn = 'Идет снег' 
            else: warn = ''
            
            fmt='%H:%M'
            
            w = _weather_id(weather_id)
            wi = _wind(wind)
            
            s = f'Сейчас в городе {name} -  {date.strftime("%H:%M %d.%m.%Y")}\n{w} {desc}\nЗа бортом {temp} градусов\nРассвет в {sunrise.strftime(fmt)} Закат в {sunset.strftime(fmt)}\n{wi} {wind} м/с\n{warn}'

            return s
        else: return 'Твой город не найден'

    def inline_weather(self, city):
        url1 = 'https://api.openweathermap.org/geo/1.0/direct'
        params = {
            'q':city,
            'appid':default_params['appid']
            }
        
        c = self.r.get(url=url1, params=params).json()

        if len(c) > 0:
            lat = c[0]['lat']
            lon = c[0]['lon']
        
        
        

