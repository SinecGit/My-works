from loader import bot, logger
from telebot import types
from telebot.types import Message
from telegram_bot_calendar import DetailedTelegramCalendar
from states.states import RequestFindHotel, all_user
import datetime
from config_data import config
from utils.requests import search_location, is_number
from utils.print_hotels import get_fine_hotels, get_bestdeal_hotels
from keyboards.count_key import create_kb_count


def do_get_location(message) -> None:

    logger.info('Вход в функцию do_get_location')

    bot.send_message(message.chat.id, 'Введите город поиска:')
    bot.set_state(message.from_user.id, RequestFindHotel.city_name, message.chat.id)


@bot.message_handler(state='*', commands=['stop'])
def get_city_name(message: Message) -> None:

    logger.info('Вызвана команда stop-перезапуск сервиса')

    bot.delete_state(message.from_user.id, message.chat.id)
    bot.send_message(message.chat.id, 'Сервис перезапущен.')


@bot.message_handler(state=RequestFindHotel.city_name)
def get_city_name(message: Message) -> None:

    logger.info('Вход в функцию get_city_name')

    if not message.text.isdigit():
        get_location(message)
    else:
        bot.send_message(message.chat.id, 'Название города должно содержать буквы')
        bot.send_message(message.chat.id, 'Введите город поиска:')


# Получение уточненной локации по введенному городу
def get_location(message) -> None:

    logger.info('Вход в функцию get_location - Получение уточненной локации по введенному городу')
    logger.debug('Введена локация: {}'.format(message.text))

    detail_location = search_location(message.text)
    kb = types.InlineKeyboardMarkup()

    if not detail_location:
        logger.info('> get_location - Указанный город не найден')

        bot.send_message(message.chat.id, 'Указанный город не найден, повторите ввод', reply_markup=kb)
        do_get_location(message)
    else:
        for kb_item in detail_location.items():
            if len(str(kb_item[0]+'='+kb_item[1]).encode('utf-8')) < 64:
                kb.add(types.InlineKeyboardButton(kb_item[0], callback_data=str(kb_item[0]+'='+kb_item[1])))

        bot.send_message(message.chat.id, '🌍 Уточните место поиска...', reply_markup=kb)


# Запросы дат заезда и выезда
def get_date_in(message) -> None:
    logger.info('Вход в функцию get_date_in')

    bot.send_message(message.chat.id, 'Выберете дату заезда в отель')
    calendar, step = DetailedTelegramCalendar(min_date=datetime.date.today()).build()
    bot.send_message(message.chat.id, f'Выберите {config.STEPS[step]}', reply_markup=calendar)


def get_date_out(message) -> None:
    logger.info('Вход в функцию get_date_out')

    min_date = datetime.datetime.strptime(all_user[message.chat.id].date_in, "%Y-%m-%d").date()

    bot.send_message(message.chat.id, 'Выберете дату выезда из отеля')
    calendar, step = DetailedTelegramCalendar(min_date=min_date).build()
    bot.send_message(message.chat.id, f'Выберите {config.STEPS[step]}', reply_markup=calendar)


# Получение данных по количеству отелей при выводе результата

def get_count_hotels(message) -> None:

    logger.info('Вход в функцию get_count_hotels')

    bot.send_message(message.chat.id, 'Количество отображаемых отелей в результате?',
                     reply_markup=create_kb_count(config.SYSTEM_PARAM['max_limit_hotels'], step=2))


# Запрос о показе фото отелей
def get_photo(message) -> None:

    logger.info('Вход в функцию get_photo - Запрос о показе фото отелей')

    kb = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text='✅  Да', callback_data='yes_photo')
    key_no = types.InlineKeyboardButton(text='❌  Нет', callback_data='no_photo')
    kb.add(key_yes, key_no)
    bot.send_message(message.chat.id, 'Показывать фото отелей?', reply_markup=kb)


# Запрос о количестве отображаемых фото
def get_count_photo(message) -> None:

    logger.info('Вход в функцию get_count_photo - Запрос о количестве отображаемых фото')

    bot.send_message(message.chat.id, 'Количество отображаемых фото отелей?',
                     reply_markup=create_kb_count(config.SYSTEM_PARAM['max_limit_photo'], step=2))


#-------------------------------------------------------------------------------
# Обработчики callback_query и message_handler
#-------------------------------------------------------------------------------

#Обработчик запроса количества фото отелей в результате
@bot.callback_query_handler(func=lambda call: call.message.text == 'Количество отображаемых фото отелей?')
def callback_set_hotels_count(call) -> None:
    bot.answer_callback_query(call.id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
    bot.edit_message_text('Отображаемых фото: {}'.format(call.data), call.message.chat.id, call.message.id)
    all_user[call.message.chat.id].count_photo = int(call.data)

    logger.debug('Количество отображаемых фото: {}'.format(int(call.data)))

    if all_user[call.message.chat.id].user_command == 'bestdeal':
        bot.set_state(call.from_user.id, RequestFindHotel.min_price, call.message.chat.id)
        bot.send_message(call.message.chat.id, 'Введите минимальную стоимость:')
    else:
        get_fine_hotels(call.message)


# Обработчик запроса на показ фото отелей
@bot.callback_query_handler(func=lambda call: call.message.text == 'Показывать фото отелей?')
def callback_set_hotels_count(call) -> None:
    bot.answer_callback_query(call.id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)

    logger.debug('>callback_set_hotels_count - Запрос о показе фото - ответ: {}'.format(call.data))

    if call.data == 'yes_photo':
        all_user[call.message.chat.id].photo = True
        call.data = 'Да'
        bot.edit_message_text('Показывать фото: {}'.format(call.data), call.message.chat.id, call.message.id)
        # Запрос о количестве фото отелей
        get_count_photo(call.message)
    else:
        all_user[call.message.chat.id].photo = False
        call.data = 'Нет'
        bot.edit_message_text('Показывать фото: {}'.format(call.data), call.message.chat.id, call.message.id)

        if all_user[call.message.chat.id].user_command == 'bestdeal':
            bot.set_state(call.from_user.id, RequestFindHotel.min_price, call.message.chat.id)
            bot.send_message(call.message.chat.id, 'Введите минимальную стоимость:')
        else:
            get_fine_hotels(call.message)


#Обработчики для ввода макс. и мин. стоимости за номер и дистанцию от центра города
@bot.message_handler(state=RequestFindHotel.min_price)
def get_min_price(message: Message) -> None:
    logger.info('> get_min_price - Запрос минимальной стоимости номера.')

    if message.text.isdigit() and int(message.text) >= 0:
        all_user[message.chat.id].price_min = int(message.text)
        bot.set_state(message.from_user.id, RequestFindHotel.max_price, message.chat.id)
        bot.send_message(message.chat.id, 'Минимальная стоимость: {}'.format(message.text))
        bot.send_message(message.chat.id, 'Введите максимальную стоимость:')
    else:
        bot.send_message(message.chat.id, 'Стоимость может быть только числом и неотрицательным.')
        bot.send_message(message.chat.id, 'Введите минимальную стоимость:')


@bot.message_handler(state=RequestFindHotel.max_price)
def get_max_price(message: Message) -> None:
    logger.info('> get_max_price - Запрос максимальной стоимости номера.')

    if message.text.isdigit() and int(message.text) >= all_user[message.chat.id].price_min:
        all_user[message.chat.id].price_max = int(message.text)
        bot.set_state(message.from_user.id, RequestFindHotel.min_distance, message.chat.id)
        bot.send_message(message.chat.id, 'Максимальная стоимость: {}'.format(message.text))
        bot.send_message(message.chat.id, 'Введите минимальное расстояние от центра города, км:')
    else:
        bot.send_message(message.chat.id, 'Стоимость может быть только числом и не меньше минимальной стоимости')
        bot.send_message(message.chat.id, 'Введите максимальную стоимость:')


@bot.message_handler(state=RequestFindHotel.min_distance)
def get_min_distance(message: Message) -> None:
    logger.info('> get_min_distance - Запрос мин. дистанции отеля от центра.')

    if is_number(message.text) and float(message.text) >= 0:
        all_user[message.chat.id].distance_min = float(message.text)
        bot.set_state(message.from_user.id, RequestFindHotel.max_distance, message.chat.id)
        bot.send_message(message.chat.id, 'Минимальное расстояние от центра города: {} км'.format(message.text))
        bot.send_message(message.chat.id, 'Введите максимальное расстояние от центра города, км:')
    else:
        bot.send_message(message.chat.id, 'Расстояние может быть только числом и неотрицательным')
        bot.send_message(message.chat.id, 'Введите минимальное расстояние от центра города, км:')


@bot.message_handler(state=RequestFindHotel.max_distance)
def get_max_distance(message: Message) -> None:
    logger.info('> get_max_distance - Запрос макс. дистанции отеля от центра.')

    if is_number(message.text) and float(message.text) >= all_user[message.chat.id].distance_min:
        all_user[message.chat.id].distance_max = float(message.text)
        bot.send_message(message.chat.id, 'Максимальное расстояние от центра города: {} км'.format(message.text))

        bot.set_state(message.from_user.id, RequestFindHotel.max_distance, message.chat.id)
        bot.delete_state(message.from_user.id, message.chat.id)
        # get_fine_hotels(message)
        get_bestdeal_hotels(message)
    else:
        bot.send_message(message.chat.id, 'Расстояние может быть только числом и не меньше минимального')
        bot.send_message(message.chat.id, 'Введите максимальное расстояние от центра города, км:')


# Обработчик отображения количества отелей в результате
@bot.callback_query_handler(func=lambda call: call.message.text == 'Количество отображаемых отелей в результате?')
def callback_set_hotels_count(call) -> None:
    logger.debug('>callback_set_hotels_count - Колич. отображаемых отелей: {}'.format(call.data))
    bot.answer_callback_query(call.id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
    bot.edit_message_text('Количество отображаемых отелей: {}'.format(call.data),
                          call.message.chat.id, call.message.id)

    all_user[call.message.chat.id].count_hotels = int(call.data)
    # Запрос о показе фото отелей (Да/Нет)
    get_photo(call.message)


# Обработчик уточнения локации по введенному городу
@bot.callback_query_handler(func=lambda call: call.message.text == '🌍 Уточните место поиска...')
def callback_set_location(call) -> None:

    logger.debug('> callback_set_location - место поиска: {}'.format(call.data))

    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
    bot.edit_message_text('Место поиска: {}'.format(call.data.split('=')[0]),
                          call.message.chat.id, call.message.id)

    bot.answer_callback_query(call.id)

    all_user[call.message.chat.id].city_name = call.data.split('=')[0].rstrip()
    all_user[call.message.chat.id].city_id = call.data.split('=')[1].rstrip()

    bot.set_state(call.from_user.id, RequestFindHotel.date_in, call.message.chat.id)

    # Запрос даты заезда в отель
    all_user[call.message.chat.id].date_in = ''
    all_user[call.message.chat.id].date_out = ''

    get_date_in(call.message)


# обработчик календаря
@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def cal(c):
    if all_user[c.message.chat.id].date_in:
        min_date = datetime.datetime.strptime(all_user[c.message.chat.id].date_in, "%Y-%m-%d").date()
    else:
        min_date = datetime.date.today()

    result, key, step = DetailedTelegramCalendar(min_date=min_date, locale='ru').process(c.data)

    if not result and key:
        bot.edit_message_text(f"Выберите {config.STEPS[step]}",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif result:

        bot.edit_message_text(f"Выбрана дата: {result.strftime('%d-%m-%Y')}",
                              c.message.chat.id,
                              c.message.message_id)

        bot.answer_callback_query(c.id)

        if result:
            if all_user[c.message.chat.id].date_in:
                all_user[c.message.chat.id].date_out = str(result)
                logger.debug('>calendar - дата выезда: {}'.format(all_user[c.message.chat.id].date_out))

                get_count_hotels(c.message)
            else:
                all_user[c.message.chat.id].date_in = str(result)
                logger.debug('>calendar - дата заезда: {}'.format(all_user[c.message.chat.id].date_in))

                get_date_out(c.message)
