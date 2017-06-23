import time
import telepot
from telepot.loop import MessageLoop
import sqlite3
import configparser
import os


cur_dir = os.path.dirname(os.path.abspath(__file__))

config = configparser.ConfigParser()
config.read(cur_dir+'/config.ini')
con = sqlite3.connect(cur_dir+'/'+config['sqlite']['db_name'], check_same_thread=False)
cursor = con.cursor()

message_with_inline_keyboard = None


def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)

    command = msg['text'].strip().lower().split(" ")[0]
    value = msg['text'].strip().lower().split(" ")[-1]

    if command == '/start' or command == '/stop':
        print(command)
        command_to_notify = {
            '/start': 1,
            '/stop': 0,
        }
        cursor.execute("UPDATE user SET notify = ? WHERE id = ?",
                       (command_to_notify[command], chat_id,))
        con.commit()

    if command == '/help':
        bot.sendMessage(chat_id, 'Команды: \n/minprice \n/maxprice \n/setrooms')
    if command == '/minprice':
        if value != '/minprice':
            cursor.execute("UPDATE user SET minprice = ? WHERE id = ?",
                           (value, chat_id))
            con.commit()
            bot.sendMessage(chat_id, 'Ищем квартиры от $%s' % value)
        else:
            bot.sendMessage(chat_id, 'Введите минимальную цену. Пример: /minprice 150')
    if command == '/maxprice':
        if value != '/maxprice':
            cursor.execute("UPDATE user SET maxprice = ? WHERE id = ?",
                           (value, chat_id))
            con.commit()
            bot.sendMessage(chat_id, 'Ищем квартиры до $%s' % value)
        else:
            bot.sendMessage(chat_id, 'Введите максимальную цену. Пример: /maxprice 500')
    if command == '/setrooms':
        if value != '/setrooms':
            cursor.execute("UPDATE user SET rooms = ? WHERE id = ?",
                           (value, chat_id))
            con.commit()
            bot.sendMessage(chat_id, 'Ищем %s-х комнатные квартиры' % value)
        else:
            bot.sendMessage(chat_id, 'Пример: /setrooms 2')

bot = telepot.Bot(config['bot']['token'])

MessageLoop(bot, {'chat': on_chat_message}).run_as_thread()
print('Listening ...')

# Keep the program running.
while 1:
    time.sleep(10)

