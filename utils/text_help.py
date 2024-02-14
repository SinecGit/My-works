from loader import logger


# Информация о возможностях бота
def print_help() -> str:

    logger.info('Вход в функцию print_help - список команд бота')

    txt_help = '*Список команд:*\n' \
                '\n/lowprice - вывод самых дешёвых отелей в городе\n' \
                '\n/highprice - вывод самых дорогих отелей в городе\n' \
                '\n/bestdeal - вывод отелей, наиболее подходящих по цене и расположению от центра\n' \
                '\n/history - вывод истории поиска отелей\n' \
                '\n/start - вывод стартового экрана\n'

    return txt_help
