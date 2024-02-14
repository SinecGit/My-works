from telebot.handler_backends import State, StatesGroup
from loader import logger


class RequestFindHotel(StatesGroup):
    command = State()
    city_name = State()
    min_price = State()
    max_price = State()
    min_distance = State()
    max_distance = State()
    date_in = State()
    date_out = State()

    # chat_id = State()
    # user_id = State()
    # city_id = State()
    # hotels_count = State()
    # view_photo = State()
    # photo_count = State()


class Users:
    def __init__(self) -> None:
        self.msg = None
        self.username = None
        self.user_id = None
        self.chat_id = None
        self.date_in = None
        self.date_out = None
        self.city_name = None
        self.city_id = None
        self.count_hotels = None
        self.photo = None
        self.count_photo = None
        self.price_min = None
        self.price_max = None
        self.distance_min = None
        self.distance_max = None
        self.user_command = None
        self.current_msg_id = None
        self.list_hotels = []


all_user = dict()


def set_user_id(message):

    logger.info('Установка состояний бота')

    user_name = []

    all_user[message.chat.id] = Users()
    all_user[message.chat.id].msg = message
    all_user[message.chat.id].user_id = message.chat.id

    if message.from_user.username:
        user_name.append(message.from_user.username)
    if message.from_user.first_name:
        user_name.append(message.from_user.first_name)
    if message.from_user.last_name:
        user_name.append(message.from_user.last_name)

    all_user[message.chat.id].username = ' '.join(user_name)

