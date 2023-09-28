
import requests

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

        l = []
        if self.data['cod'] == '200':
            for t in self.data['list']:
                s = f'--> {t["dt_txt"]} <------\nТемпература {t["main"]["temp"]}\nПогода {t["weather"][0]["description"].capitalize()}\nВетер {t["wind"]["speed"]}\nОсадки {t["pop"]}'
                l.append(s)
            
            return '\n'.join(l)
        else: return f'Твой город не найден. /city чтобы добавить свой город'

if __name__ == "__main__":
    t = Forecast()
    t.get_weather('Санкт-Петербург')
    print(t.parse_html())