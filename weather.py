
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
        for t in self.data['list']:
            s = f'Погода {t["dt_txt"]} Температура {t["main"]["temp"]} Погода {t["weather"][0]["description"].capitalize()} Ветер {t["wind"]["speed"]} Осадки {t["pop"]}'
            l.append(s)
            
        return ''.join(l)

if __name__ == "__main__":
    t = Forecast()
    t.get_weather('Санкт-Петербург')
    print(t.parse_html())