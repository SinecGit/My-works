from telebot import types
from loader import logger


# Создание Inline-кнопок для ответов за запросы
def create_kb_count(count, step=2) -> types.InlineKeyboardMarkup:
    logger.info('Вход в функцию Создание Inline-кнопок для ответов за запросы')

    kb = types.InlineKeyboardMarkup()
    kb_list = []

    for kb_item in range(2, count + 2, step):
        kb_list += [types.InlineKeyboardButton(kb_item, callback_data=kb_item)]

    kb.add(*kb_list)

    return kb

