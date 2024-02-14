from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from config_data import config
from loguru import logger

# Инициализация бота
# storage = StateMemoryStorage()
# bot = TeleBot(token=config.BOT_TOKEN, state_storage=storage)
bot = TeleBot(token=config.BOT_TOKEN)
logger.info('Загружен токен бота для ТГ')
