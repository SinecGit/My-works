from loader import bot, logger
from telebot.types import Message
from utils.text_help import print_help


@bot.message_handler(commands=['help'])
def command_help(message: Message) -> None:
    logger.info('Вызвана команда: {}'.format(message.text))

    bot.send_message(message.chat.id, text=print_help(), parse_mode='Markdown')
