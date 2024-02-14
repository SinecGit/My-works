import sqlite3
from states.states import all_user
from datetime import datetime
from loader import logger


class BotDB:

    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def user_exists(self, user_id):
        """Проверяем, есть ли пользователь в базе"""
        result = self.cursor.execute('SELECT user_id FROM BotTable WHERE user_id = ?', (user_id,))

        return bool(len(result.fetchall()))

    @logger.catch()
    def add_record(self, user_id):
        """Создаем запись истории поиска"""
        # print(all_user[user_id].user_id, all_user[user_id].username, all_user[user_id].user_command)
        # print(user_id)

        try:
            self.cursor.execute('INSERT INTO BotTable (user_id, user_name, user_cmd, dt, list_hotels, '
                                'location, period, date)'
                                'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                                (all_user[user_id].user_id,
                                 all_user[user_id].username,
                                 all_user[user_id].user_command,
                                 datetime.now().strftime('%d-%m-%Y %H:%M:%S'),
                                 '^'.join(all_user[user_id].list_hotels),
                                 all_user[user_id].city_name,
                                 datetime.strftime(datetime.strptime(all_user[user_id].date_in, '%Y-%m-%d'), '%d-%m-%Y') +
                                 '^' + datetime.strftime(datetime.strptime(all_user[user_id].date_out, '%Y-%m-%d'), '%d-%m-%Y'),
                                 datetime.now().strftime('%Y-%m-%d'),))

            all_user[all_user[user_id].user_id].list_hotels = []
            logger.info('Выполнено добавление записи в БД')

            return self.conn.commit()

        except sqlite3.IntegrityError as e:
            logger.error('Ошибка записи в БД!')

            print("Error occurred: ", e)
            # self.close()

    def get_records(self, user_id, within='key_all'):
        """Получаем историю о командах пользователя"""

        if within == 'key_day':
            logger.info('Получение записей истории за день')

            result = self.cursor.execute('SELECT * FROM BotTable WHERE user_id = ? '
                                         'AND date BETWEEN DATE("now", "start of day") '
                                         'AND DATE("now", "localtime") ORDER BY date', (user_id,))
        elif within == 'key_week':
            logger.info('Получение записей истории за неделю')

            result = self.cursor.execute('SELECT * FROM BotTable WHERE user_id = ? '
                                         'AND date BETWEEN DATE("now", "-6 day") '
                                         'AND DATE("now", "localtime") ORDER BY date', (user_id,))
        elif within == 'key_month':
            logger.info('Получение записей истории за месяц')

            result = self.cursor.execute('SELECT * FROM BotTable WHERE user_id = ? '
                                         'AND date BETWEEN DATE("now", "start of month") '
                                         'AND DATE("now", "localtime") ORDER BY date', (user_id,))
        else:
            logger.info('Получение всех записей в истории')

            result = self.cursor.execute('SELECT * FROM BotTable WHERE user_id = ?', (user_id,))

        return result.fetchall()

    def close(self):
        logger.info('Закрытие БД')
        """Закрываем соединение с БД"""
        self.conn.close()
