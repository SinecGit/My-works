from loader import bot, logger
import handlers
from telebot.custom_filters import StateFilter
from utils.set_bot_commands import set_default_commands
from datetime import datetime
from database.db import BotDB


UserBotDB = BotDB('database/userdb.db')

if __name__ == '__main__':

    bot.send_message(1551250217, 'Запуск сервиса: {}'.format(datetime.now().strftime('%d-%m-%Y %H:%M:%S')))
    bot.add_custom_filter(StateFilter(bot))

    set_default_commands(bot)
    logger.add('log/botlog.log', level='DEBUG', rotation='500 KB', compression='zip', encoding='utf-8')
    logger.info('Запуск бота')

    bot.infinity_polling()

    