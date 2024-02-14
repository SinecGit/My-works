from loader import bot, logger
from states.states import RequestFindHotel, all_user, set_user_id
from telebot.types import Message, CallbackQuery
from telebot import types
from handlers.lowprice import onkey_lowprice
from handlers.highprice import onkey_highprice
from handlers.bestdeal import onkey_bestdeal
from handlers.history import onkey_history
from handlers.help import command_help


@bot.message_handler(commands=['start'])
def command_start(message: Message) -> None:

    set_user_id(message)
    logger.debug('Запуск от пользователя: {} id= {}'.format(all_user[message.chat.id].username, message.from_user.id))

    bot.send_message(message.chat.id, 'Мой ID {}'.format(message.from_user.id))
    bot.send_message(1551250217, 'Вошел пользователь с ID {}'.format(message.from_user.id))

    # print('Пользователь: {} с ID: {}'.format(all_user[message.chat.id].username, message.from_user.id))

    bot.set_state(message.from_user.id, RequestFindHotel.command, message.chat.id)

    file_photo_start = open('resources/main_page.jpg', 'rb')

    logger.info('Команда Start и вывод главного меню')

    keyboard_start = types.InlineKeyboardMarkup()

    key_lowprice = types.InlineKeyboardButton(text='Недорогие отели', callback_data="lowprice")
    key_highprice = types.InlineKeyboardButton(text='Дорогие отели', callback_data="highprice")
    key_bestdeal = types.InlineKeyboardButton(text='Оптимальные отели', callback_data="bestdeal")
    key_history = types.InlineKeyboardButton(text='История поиска', callback_data="history")
    key_help = types.InlineKeyboardButton(text='Мои возможности', callback_data="help")

    keyboard_start.add(key_lowprice, key_highprice)
    keyboard_start.add(key_bestdeal, key_history)
    keyboard_start.add(key_help)

    bot.send_photo(message.from_user.id, photo=file_photo_start,
                   caption='Привет ✌, я Бот-помощник, помогу тебе выбрать самый лучший отель, '
                           'для незабываемого отдыха, с чего начнем поиск?', reply_markup=keyboard_start)


@bot.message_handler(content_types=['text'])
def command_start(message: Message) -> None:
    logger.debug('Ввод неверной команды: {}'.format(message.text))
    bot.send_message(message.chat.id, 'Не знаю такой команды! Список команд /help.')


@bot.callback_query_handler(func=lambda c: True)
def get_command(c: CallbackQuery) -> None:

    bot.answer_callback_query(c.id)
    all_user[c.message.chat.id].user_command = c.data

    logger.debug('Нажата кнопка (команда): {}', format(c.data))

    if c.data == "lowprice":
        onkey_lowprice(c.message)

    elif c.data == "highprice":
        onkey_highprice(c.message)

    elif c.data == "bestdeal":
        onkey_bestdeal(c.message)

    elif c.data == "history":
        onkey_history(c.message)

    elif c.data == "help":
        command_help(c.message)



