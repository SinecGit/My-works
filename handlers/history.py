from loader import bot, logger
from telebot.types import Message, CallbackQuery
from telebot import types
from config_data.config import HISTORY_PERIOD
from states.states import all_user, set_user_id, Users
from main import UserBotDB


@bot.message_handler(commands=['history'])
def command_lowprice(message: Message) -> None:
    logger.info('Вызвана команда: {}'.format(message.text))

    if message.chat.id not in all_user:
        set_user_id(message)

    all_user[message.chat.id].user_command = message.text[1:]

    ask_history(message)


def onkey_history(message: Message):
    ask_history(message)


def ask_history(message):

    keyboard_start = types.InlineKeyboardMarkup()

    key_day = types.InlineKeyboardButton(text='За день', callback_data="key_day")
    key_week = types.InlineKeyboardButton(text='За неделю', callback_data="key_week")
    key_month = types.InlineKeyboardButton(text='За месяц', callback_data="key_month")
    key_all = types.InlineKeyboardButton(text='За все время', callback_data="key_all")

    keyboard_start.add(key_day, key_week, key_month, key_all)

    bot.send_message(message.chat.id, 'За какой период вывести историю поиска?', reply_markup=keyboard_start)


@bot.callback_query_handler(func=lambda c: c.message.text == 'За какой период вывести историю поиска?')
def show_history(c: CallbackQuery) -> None:

    logger.info('Выбран период истории: {}'.format(c.data))

    bot.answer_callback_query(c.id)
    result = UserBotDB.get_records(c.message.chat.id, c.data)

    logger.debug('По выбранному периоду найдено записей: {}'.format(len(result)))

    bot.send_message(c.message.chat.id, 'Период истории: {}'.format(HISTORY_PERIOD[c.data]))

    if UserBotDB.user_exists(c.message.chat.id):
        if result:
            bot.send_message(c.message.chat.id, 'История поиска...')
            for i_idx, item in enumerate(result, 1):
                out_str = '*Запись: {}*\n\n'\
                          'Команда: *{}*\n' \
                          'Дата и время: *{}*\n'\
                          'Место поиска: *{}*\n'\
                          'Период: *c {} по {}*\n'\
                          'Найденные отели:\n{}'.format(i_idx, item[3], item[4], item[6],
                                                        item[7].split('^')[0], item[7].split('^')[1],
                                                        ''.join(['👉 {}. {}\n'.format(index, elem) for index, elem in
                                                        enumerate(item[5].split('^'), 1)]))

                bot.send_message(c.message.chat.id, out_str, parse_mode='Markdown', disable_web_page_preview=True)
            bot.send_message(c.message.chat.id, 'Вывод истории завершен.')
        else:
            bot.send_message(c.message.chat.id, 'Нет истории за выбранный период!'.format(c.message.chat.id))
    else:
        bot.send_message(c.message.chat.id, 'У пользователя: {} пока нет истории!'.format(c.message.chat.id))
