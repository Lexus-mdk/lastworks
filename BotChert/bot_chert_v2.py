import requests
import telebot
import time
import threading
import schedule

# Зареганные пользователи реал тайм (да, мне лень было разбираться с бд)
auth_users = {
    'user_id': {'password': '', 'token': '', 'login': '', 'notif': 'False'}
}
# Пользователи самой системы
users = {
    'login': {'password': 'password', 'token': '', 'notif': 'False'},
    'Вася': {'password': '1234', 'token': '', 'notif': 'False'}
}


# Авторизация
def auth(message):
    data = message.text.split(' ')
    try:
        login = data[0]
        password = data[1]
    except IndexError:
        login = ''
        password = ''
    if login in users and password == users[login]['password']:
        auth_users[str(message.chat.id)] = users[login]
        bot.send_message(message.chat.id, "Всё в порядке, можешь пользоваться) Введи /start")
    else:
        msg = bot.send_message(message.chat.id, "Неверный login или пароль, введи снова")
        bot.register_next_step_handler(msg, auth)


# Выход из акка
def logout(message):
    if auth_users[message.chat.id]['notif'] == True:
        break_notifications(message)
    del auth_users[str(message.chat.id)]
    msg = bot.send_message(message.chat.id, "Ты вышел из аккаунта, введи логин и пароль, чтобы снова зайти")
    bot.register_next_step_handler(msg, auth)


# Вывод команд
def commands(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton('Включить уведомления', callback_data='start notifications'),
        telebot.types.InlineKeyboardButton('Выключить уведомления', callback_data='break notifications')
    )
    keyboard.row(
        telebot.types.InlineKeyboardButton('Просмотреть статистику', callback_data='statistic'),
        telebot.types.InlineKeyboardButton('Разлогиниться', callback_data='logout')
    )
    bot.send_message(message.chat.id, "Команды:\n" + ',\n'.join(commands), reply_markup=keyboard)


# Вывод статистики - кидается гет запрос на сервер
def statistic(message):
    #     headers = {
    #         'Token': auth_users[message.chat.id]['token']
    #     }
    #     req = requests.get("/api/files/statistic", headers=headers)
    #     src = req.json()
    #     # Надо бы ещё предобработать полученный жсончик
    bot.send_message(message.chat.id, 'Статистика:\nФайлов загружено - 1\nОбщий размер - 1.2 Гб')


# Запрос на сервер, для уведомлений
def get_request(message):
    #     headers = {
    #         'Token': auth_users[message.chat.id]['token']
    #     }
    #     req = requests.get("/api/files/statistic", headers=headers)
    #     src = req.json()
    #     # Надо бы ещё предобработать полученный жсончик
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton('Выключить', callback_data='break notifications')
    )
    bot.send_message(message.chat.id, 'Уведомление пришло', reply_markup=keyboard)


# Тупо каждые n секунд будет кидаться запрос на сервер (выдача надеюсь json буит),
# проверяется, есть ли новое уведомление и берется инфа. Работает, пока не ввести команду break notifications
def get_notif(message):
    auth_users[str(message.chat.id)]['notif'] = True
    schedule.every(10).seconds.do(get_request, message)
    while auth_users[str(message.chat.id)]['notif'] == True:
        schedule.run_pending()
        time.sleep(1)
    print('Машина по уничтожению человечества была отключена')


#  Запускает машину убийства (уведомления)
def start_notifications(message):
    if auth_users[str(message.chat.id)]['notif'] == True:
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(
            telebot.types.InlineKeyboardButton('Выключить', callback_data='break notifications')
        )
        bot.send_message(message.chat.id, 'Уведомления уже работают', reply_markup=keyboard)
    else:
        job_thread = threading.Thread(target=get_notif(message))
        job_thread.start()


# Останавливает терминатора (уведомления)
def break_notifications(message):
    auth_users[str(message.chat.id)]['notif'] = False
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton('Включить', callback_data='start notifications')
    )
    bot.send_message(message.chat.id, 'Уведомления отключены', reply_markup=keyboard)


# Основная функция запуска чертилы
def telegram_bot():
    #     Начальная команда
    @bot.message_handler(commands=["start"])
    def start_message(message):
        if str(message.chat.id) in auth_users:
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.row(
                telebot.types.InlineKeyboardButton('Commands', callback_data='commands')
            )
            bot.send_message(message.chat.id,
                             "Привет, я Бот-Черт. Напиши 'Commands', чтобы узнать список комманд)\nЛибо нажми на кнопку ;)",
                             reply_markup=keyboard
                             )
        else:
            msg = bot.send_message(message.chat.id, "Привет, отправь login и пароль через пробел (login password)")
            bot.register_next_step_handler(msg, auth)

    #     Обработчик сообщений
    @bot.message_handler(content_types=["text"])
    def send_text(message):
        if str(message.chat.id) in auth_users:
            msgl = message.text.lower()
            print(msgl)
            if msgl in commands:
                commands[msgl](message)
            else:
                bot.send_message(message.chat.id, "Неизвестная команда, проверьте список:\n" + ',\n'.join(commands))
        else:
            msg = bot.send_message(message.chat.id, "Привет, отправь login и пароль через пробел (login password)")
            bot.register_next_step_handler(msg, auth)

    #     Обработчик кнопок
    @bot.callback_query_handler(func=lambda call: True)
    def iq_callback(query):
        if str(query.message.chat.id) in auth_users:
            func_name = query.data
            bot.answer_callback_query(query.id)
            print(func_name)
            commands[func_name](query.message)
        else:
            msg = bot.send_message(query.message.chat.id,
                                   "Привет, отправь login и пароль через пробел (login password)")
            bot.register_next_step_handler(msg, auth)

    bot.polling(none_stop=True)


# Словарь с командами:функциями
commands = {
    'commands': commands,
    'statistic': statistic,
    'start notifications': start_notifications,
    'break notifications': break_notifications,
    'logout': logout
}

if __name__ == '__main__':
    bot = telebot.TeleBot('токен)))')
    telegram_bot()