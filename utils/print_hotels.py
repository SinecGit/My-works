from loader import bot, logger
from telebot import types
from config_data import config
from states.states import all_user
from utils.requests import do_search_hotels, do_search_photo
import datetime
from main import UserBotDB


# Функция поиска отелей по заданным критериям lowprice / highprice
def get_fine_hotels(message):
    logger.info('Вход в функцию get_fine_hotels')

    mess = bot.send_message(message.chat.id, 'Ищу подходящие отели...🔎')
    hotels_list = do_search_hotels(message)

    logger.debug('>get_fine_hotels - Найденных отелей:{}'.format(len(hotels_list)))

    idx = 0

    # print(json.dumps(result, indent=10, ensure_ascii=False))
    price_hotel_ue = config.SYSTEM_PARAM['currency']['RU']

    days_count = (datetime.datetime.strptime(all_user[message.chat.id].date_out, '%Y-%m-%d') -
                  datetime.datetime.strptime(all_user[message.chat.id].date_in, '%Y-%m-%d')).days

    logger.debug('> get_fine_hotels - Количество ночей в отеле:{}'.format(days_count))

    suffix = ''

    if 4 < days_count < 21:
        suffix = 'ночей'
    elif days_count % 10 == 1:
        suffix = 'ночь'
    elif days_count % 10 == 0:
        suffix = 'ночей'
    elif days_count % 10 in [2, 3, 4]:
        suffix = 'ночи'
    elif days_count % 10 > 4:
        suffix = 'ночей'

    bot.edit_message_text('Вот что я нашел:👇', mess.chat.id, mess.id)

    for i_index, i_item in enumerate(hotels_list, 1):
        idx += 1
        name_hotel = i_item['name']
        address_hotel = [i_item['address']['countryName'],
                         i_item['address']['locality'],
                         ]
        distance_center = i_item['landmarks'][0]['distance']

        if 'ratePlan' in i_item:
            price_hotel = str('{:,}'.format(i_item['ratePlan']['price']['exactCurrent'])) + ' ' + price_hotel_ue
            all_price_hotel = str('{:,.2f}'.format(i_item['ratePlan']['price']['exactCurrent'] * days_count)) + price_hotel_ue
        else:
            price_hotel = 'Не указана'
            all_price_hotel = 'Не указана'

        if 'postalCode' in i_item['address']:
            address_hotel.append(i_item['address']['postalCode'])

        if 'streetAddress' in i_item['address']:
            address_hotel.append(i_item['address']['streetAddress'])

        text_url_hotel = '[{}]({})'.format(name_hotel, config.SYSTEM_PARAM['url_hotel'] + str(i_item['id']))

        text_info = '{}. *Информация об отеле* \n\n'\
                    '*Название:* {} \n'\
                    '*Адрес:* {} \n'\
                    '*Удаленность от центра:* {} \n'\
                    '*Стоимость номера:* {}\n'\
                    '*Стоимость проживания за {} {}:* {}'.\
            format(i_index, text_url_hotel, ', '.join(address_hotel), distance_center, price_hotel,
                   days_count, suffix, all_price_hotel)

        if all_user[message.chat.id].photo:
            media_group = list()

            # отправка запроса на получение фото отеля
            photo_list = do_search_photo(i_item['id'], message)

            for i_idx, i_photo in enumerate(photo_list):
                if i_idx == 0:
                    media_group.append(types.InputMediaPhoto(i_photo['baseUrl'].format(size=i_photo['sizes'][0]['suffix']),
                                                             caption=text_info, parse_mode='Markdown'))
                else:
                    media_group.append(types.InputMediaPhoto(i_photo['baseUrl'].format(size=i_photo['sizes'][0]['suffix'])))

            bot.send_media_group(message.chat.id, media_group)
            all_user[message.chat.id].list_hotels.append(text_url_hotel)

        else:
            bot.send_message(message.chat.id, text_info, parse_mode='Markdown', disable_web_page_preview=True)
            all_user[message.chat.id].list_hotels.append(text_url_hotel)

    if idx == 0:
        bot.send_message(message.chat.id, 'По вашему запросу ничего не найдено.')
        logger.info('> get_fine_hotels - По вашему запросу ничего не найдено.')

    else:
        UserBotDB.add_record(message.chat.id)
        bot.send_message(message.chat.id, 'Поиск успешно завершен.')
        logger.info('> get_fine_hotels - Поиск успешно завершен.')


# Функция поиска отелей по заданным критериям bestdeal
def get_bestdeal_hotels(message):
    logger.info('Вход в функцию get_bestdeal_hotels')

    mess = bot.send_message(message.chat.id, 'Ищу подходящие отели...🔎')
    hotels_list = do_search_hotels(message)

    logger.debug('>get_bestdeal_hotels - Найденных отелей:{}'.format(len(hotels_list)))

    price_hotel_ue = config.SYSTEM_PARAM['currency']['RU']

    days_count = (datetime.datetime.strptime(all_user[message.chat.id].date_out, '%Y-%m-%d') -
                  datetime.datetime.strptime(all_user[message.chat.id].date_in, '%Y-%m-%d')).days

    logger.debug('> get_bestdeal_hotels - Количество ночей в отеле:{}'.format(days_count))

    suffix = ''

    if 4 < days_count < 21:
        suffix = 'ночей'
    elif days_count % 10 == 1:
        suffix = 'ночь'
    elif days_count % 10 == 0:
        suffix = 'ночей'
    elif days_count % 10 in [2, 3, 4]:
        suffix = 'ночи'
    elif days_count % 10 > 4:
        suffix = 'ночей'
    idx = 0

    for i_index, i_item in enumerate(hotels_list, 1):
        dist = float(i_item['landmarks'][0]['distance'].strip(' км').replace(',', '.'))

        if all_user[message.chat.id].distance_min <= dist <= all_user[message.chat.id].distance_max:
            if idx < all_user[message.chat.id].count_hotels:
                # print(idx, ' -- ', all_user[message.chat.id].count_hotels)
                if idx == 0:
                    bot.edit_message_text('Вот что я нашел:👇', mess.chat.id, mess.id)

                idx += 1
                name_hotel = i_item['name']
                address_hotel = [i_item['address']['countryName'],
                                 i_item['address']['locality'],
                                 ]
                distance_center = i_item['landmarks'][0]['distance']

                if 'ratePlan' in i_item:
                    price_hotel = str('{:,}'.format(i_item['ratePlan']['price']['exactCurrent'])) + ' ' + price_hotel_ue
                    all_price_hotel = str('{:,.2f}'.format(i_item['ratePlan']['price']['exactCurrent'] * days_count)) + price_hotel_ue
                else:
                    price_hotel = 'Не указана'
                    all_price_hotel = 'Не указана'

                if 'postalCode' in i_item['address']:
                    address_hotel.append(i_item['address']['postalCode'])

                if 'streetAddress' in i_item['address']:
                    address_hotel.append(i_item['address']['streetAddress'])

                text_url_hotel = '[{}]({})'.format(name_hotel, config.SYSTEM_PARAM['url_hotel'] + str(i_item['id']))

                text_info = '{}. *Информация об отеле* \n\n'\
                            '*Название:* {} \n'\
                            '*Адрес:* {} \n'\
                            '*Удаленность от центра:* {} \n'\
                            '*Стоимость номера:* {}\n'\
                            '*Стоимость проживания за {} {}:* {}'.\
                    format(idx, text_url_hotel, ', '.join(address_hotel), distance_center, price_hotel,
                           days_count, suffix, all_price_hotel)

                if all_user[message.chat.id].photo:
                    media_group = list()

                    # отправка запроса на получение фото отеля
                    photo_list = do_search_photo(i_item['id'], message)

                    for i_idx, i_photo in enumerate(photo_list):
                        if i_idx == 0:
                            media_group.append(types.InputMediaPhoto(i_photo['baseUrl'].format(size=i_photo['sizes'][0]['suffix']),
                                                                     caption=text_info, parse_mode='Markdown'))
                        else:
                            media_group.append(types.InputMediaPhoto(i_photo['baseUrl'].format(size=i_photo['sizes'][0]['suffix'])))

                    bot.send_media_group(message.chat.id, media_group)
                    all_user[message.chat.id].list_hotels.append(text_url_hotel)

                else:
                    bot.send_message(message.chat.id, text_info, parse_mode='Markdown', disable_web_page_preview=True)
                    all_user[message.chat.id].list_hotels.append(text_url_hotel)
            else:
                break

    if idx == 0:
        bot.send_message(message.chat.id, 'По вашему запросу ничего не найдено.')

        logger.info('> get_bestdeal_hotels - По вашему запросу ничего не найдено.')

    else:
        UserBotDB.add_record(message.chat.id)

        logger.info('> get_bestdeal_hotels - Поиск успешно завершен.')

        bot.send_message(message.chat.id, 'Поиск успешно завершен.')
