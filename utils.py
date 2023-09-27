
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
bot_token = config.get('main', 'botapi')
w_token = config.get('main', 'OWMAPI')