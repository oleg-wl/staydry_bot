
import requests
import datetime

from utils import w_token

class Forecast:

    def __init__(self) -> None:

        self.r = requests.session()
        self.data = None

    def get_weather(self, city):
        url = 'https://api.openweathermap.org/data/2.5/forecast'
        params = {
            'appid':w_token,
            'q': city,
            'lang':'ru',
            'units':'metric',
            'cnt':4,
            'mode':'json'}
        r = requests.get(url=url,params=params)

        self.data = r.json()

        return self

    def parse_html(self):

        header = ''
        popcount = 0
        l = []
        if self.data['cod'] == '200':
            for row in self.data['list']:

                data: datetime.datetime = datetime.datetime.strptime(row['dt_txt'], '%Y-%m-%d %H:%M:%S')
                temp: float = round(row['main']['temp'], 1)
                desc: str = row['weather'][0]['description'].capitalize()
                weather_id: int = row['weather'][0]['id']
                wind: float = round(row["wind"]["speed"], 1)
                pop: float = row['pop']

                popcount += pop
                m = '\n\U0001F6B4\u200D\u2642\uFE0F Можно ехать'

                h = ''
                if (data.hour == 3) or (data.hour == 15):
                    h = '\uE026' #3
                elif (data.hour == 6) or (data.hour == 18):
                    h = '\U0001F561' # 6 часов
                elif (data.hour == 9) or (data.hour == 21):
                    h = '\uE02C' #9
                elif (data.hour == 12) or (data.hour == 24):
                    h = '\uE02F' # 12
                
                warn = 'Ветер'
                if wind > 5:
                    warn = '\uE252 Сильный ветер '

                wid = ''
                if weather_id == 800: #clear sky
                    wid = '\uE04A'
                elif weather_id in range(500,532): #rain
                    wid = '\U0001F327'
                elif weather_id in range(600, 623): #snow
                    wid = '\U0001F328'
                elif weather_id in range(800, 805):
                    wid = '\U0001F325'
                else: wid = '\u26C8'
                

                s = f'{h} в {data.hour} часов \n{wid} {desc}\nСредняя {temp}\n{warn} {wind}\nОсадки {pop}'
                l.append(s)

                
            if popcount > 3: m = '\n\U0001F327 Возьми дождевик и езжай на метре'
            msg = '\n'.join(l)
            return msg+m
        else: return f'Твой город не найден. /city чтобы добавить свой город'

if __name__ == "__main__":
    t = Forecast()
    t.get_weather('Санкт-Петербург')
    print(t.parse_html())