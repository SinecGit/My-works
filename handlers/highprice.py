from loader import bot, logger
from telebot.types import Message
from handlers.get_hotel_info import do_get_location
from states.states import Users, all_user, set_user_id


@bot.message_handler(commands=['highprice'])
def command_lowprice(message: Message) -> None:

    logger.info('Вызвана команда: {}'.format(message.text))

    if message.chat.id not in all_user:
        set_user_id(message)

    all_user[message.chat.id].user_command = message.text[1:]

    do_get_location(message)


def onkey_highprice(message: Message):
    logger.info('Вход в функцию onkey_highprice')
    do_get_location(all_user[message.chat.id].msg)
