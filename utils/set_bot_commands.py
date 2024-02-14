from telebot.types import BotCommand
from config_data.config import DEFAULT_COMMANDS
from loader import logger


def set_default_commands(bot):
    logger.info('Вход в функцию set_default_commands - загрузка команд бота в меню')

    bot.set_my_commands(
        [BotCommand(*i) for i in DEFAULT_COMMANDS]
    )
