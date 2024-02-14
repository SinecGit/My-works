import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()

API_KEY = os.getenv('RAPIDAPI_KEY')
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Ссылки, которые используются для поиска города, отеля и фотографий
API_HOST = "hotels4.p.rapidapi.com"
CITY_URL = "https://hotels4.p.rapidapi.com/locations/v2/search"
HOTEL_URL = "https://hotels4.p.rapidapi.com/properties/list"
PHOTO_URL = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

# Заголовки запроса при обращении к rapidapi.com
HEADERS = {'x-rapidapi-host': API_HOST,
           'x-rapidapi-key': API_KEY
           }

SYSTEM_PARAM = {
    'select_date': '',
    'max_limit_hotels': 10,
    'max_count_hotels_API': 25,
    'max_limit_photo': 10,
    'locale': 'ru_RU',
    'currency': {'EN': 'RUB',
                 'RU': ' руб.'},
    'url_hotel': 'https://www.hotels.com/ho'
}

STEPS = {'y': 'год', 'm': 'месяц', 'd': 'день'}

DEFAULT_COMMANDS = (('start', 'стартовый экран'),
                    ('lowprice', 'самые дешёвые отели'),
                    ('highprice', 'самые дорогие отели'),
                    ('bestdeal', 'отели, наиболее подходящие по цене и расположению от центра'),
                    ('history', 'история поиска'),
                    ('stop', 'перезапуск сервиса'),
                    ('help', 'список команд')
                    )

HISTORY_PERIOD = {'key_day': 'за день', 'key_week': 'за неделю', 'key_month': 'за месяц', 'key_all': 'зв все время'}
