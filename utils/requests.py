import json
import re
import requests
from loader import bot, logger
from states.states import all_user
from config_data import config


# Уточнение локации по введенному городу
def search_location(str_city: str) -> dict:
    detail_location = dict()
    data = ''

    logger.info('Вход в функцию search_location')
    logger.debug('Город поиска: {}'.format(str_city))

    querystring = {"query": str_city.rstrip(), "locale": config.SYSTEM_PARAM['locale']}

    try:
        response = requests.request("GET", config.CITY_URL, headers=config.HEADERS, params=querystring, timeout=10)

        if response.status_code == requests.codes.ok:
            check = re.search(r'(?<=\"CITY_GROUP\",).+?]', response.text)
            if check:
                data = json.loads(response.text)

                detail_location = {', '.join((city['name'], re.findall(r'(\w+)[\n<]', city['caption'] + '\n')[-1])):
                                       city['destinationId'] for city in data['suggestions'][0]['entities']
                                   }
            else:
                # raise ValueError('Ошибка сервера! В JSON ключи не обнаружены.')
                detail_location = None
        else:
            raise ValueError('Ошибка сервера! Статус код не "200 ОК".')

    except Exception as e:
        print('Ошибка: ', e)
        detail_location = None

    if detail_location:
        logger.debug('>search_location - найдено локаций: {}'.format(len(detail_location)))

    return detail_location


# Поиск отелей по выбранной локации (городу)
def do_search_hotels(message) -> list:
    sortorder = ''

    logger.debug('Вход в функцию do_search_hotels с командой: {}'.format(all_user[message.chat.id].user_command))

    if all_user[message.chat.id].user_command == 'lowprice':
        sortorder = 'PRICE'
    elif all_user[message.chat.id].user_command == 'highprice':
        sortorder = 'PRICE_HIGHEST_FIRST'
    elif all_user[message.chat.id].user_command == 'bestdeal':
        sortorder = 'DISTANCE_FROM_LANDMARK'

    data = dict()

    if all_user[message.chat.id].user_command == 'bestdeal':

        querystring = {
            'destinationId': all_user[message.chat.id].city_id,
            'pageNumber': '1',
            'pageSize': config.SYSTEM_PARAM['max_count_hotels_API'],
            'checkIn': all_user[message.chat.id].date_in,
            'checkOut': all_user[message.chat.id].date_out,
            'adults1': '1',
            'priceMin': all_user[message.chat.id].price_min,
            'priceMax': all_user[message.chat.id].price_max,
            'sortOrder': sortorder,
            'locale': config.SYSTEM_PARAM['locale'],
            'currency': config.SYSTEM_PARAM['currency']['EN'],
            'landmarkIds': 'City center'
        }
    else:
        querystring = {
            'destinationId': all_user[message.chat.id].city_id,
            'pageNumber': '1',
            'pageSize': all_user[message.chat.id].count_hotels,
            'checkIn': all_user[message.chat.id].date_in,
            'checkOut': all_user[message.chat.id].date_out,
            'adults1': '1',
            'sortOrder': sortorder,
            'locale': config.SYSTEM_PARAM['locale'],
            'currency': config.SYSTEM_PARAM['currency']['EN']
        }

    try:
        logger.info('Оправка запроса на сервер'
                    )
        response = requests.request("GET", config.HOTEL_URL, headers=config.HEADERS, params=querystring, timeout=10)

        if response.status_code == requests.codes.ok:
            data = json.loads(response.text)
        else:
            logger.warning('Ошибка запроса данных с сервера')

            bot.send_message(message.chat.id, 'Ошибка запроса данных с сервера, повторите поиск.')
            raise ValueError('Ошибка сервера! Статус код не "200 ОК".')

    except Exception as e:
        print('Ошибка', e)
        logger.error('Ошибка загрузки данных с сервера')

        bot.send_message(message.chat.id, 'Непредвиденная ошибка загрузки данных с сервера, повторите поиск.')
        return data

    data_hotels = data['data']['body']['searchResults']['results']

    return data_hotels


def do_search_photo(hotel_id, message) -> list:

    logger.info('Вход в функцию do_search_photo')

    querystring = {"id": hotel_id}
    response = requests.request("GET", config.PHOTO_URL, headers=config.HEADERS, params=querystring, timeout=10)

    logger.info('>do_search_photo - отправка запроса серверу')

    if response.status_code == requests.codes.ok:
        check = re.search(r'(?<=,)\"hotelImages\".+?]', response.text)

        logger.debug('Получен ответ от сервера с кодом: {}'.format(response.status_code))

        if check:
            photo_data = json.loads(response.text)
            photos_address = photo_data["hotelImages"][:all_user[message.chat.id].count_photo]

            return photos_address
        else:
            logger.warning('> do_search_photo - Ошибка запроса фото с сервера, повторите поиск.')

            bot.send_message(message.chat.id, 'Ошибка запроса фото с сервера, повторите поиск.')
            raise ValueError('Ошибка сервера! В JSON ключи не обнаружены.')
    else:
        logger.error('Непредвиденная ошибка загрузки фото с сервера, повторите поиск.')

        bot.send_message(message.chat.id, 'Непредвиденная ошибка загрузки фото с сервера, повторите поиск.')
        raise ValueError('Ошибка сервера! Статус код не "200 ОК".')


# Проверка на число
def is_number(txt_str: str) -> bool:
    logger.info('Вход в функцию is_number - проверка на число')

    try:
        float(txt_str)
        return True
    except ValueError:
        return False
