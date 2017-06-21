import json
import telepot
import sqlite3
import configparser
import os
import requests


cur_dir = os.path.dirname(os.path.abspath(__file__))

config = configparser.ConfigParser()
config.read(cur_dir+'/config.ini')

con = sqlite3.connect(cur_dir+'/'+config['sqlite']['db_name'])
cursor = con.cursor()
bot = telepot.Bot(config['bot']['token'])

def old_list():
    array = []
    cursor.execute('SELECT id FROM flatters')
    for row in cursor:
        array.append(row[0])
    return array

def new_list():
    array = []
    url = 'https://ak.api.onliner.by/search/apartments'
    response = requests.get(url)
    resp = response.json()
    apartments = resp['apartments']

    for apartment in apartments:
        array.append(apartment['id'])
    return array

def rewrite_flatters():
    cursor.execute('DELETE FROM flatters')
    con.commit()

    i = 1
    while i <= 21:
        url = 'https://ak.api.onliner.by/search/apartments?page=' + str(i)
        response = requests.get(url)
        resp = response.json()
        apartments = resp['apartments']
        i = i + 1

        for apartment in apartments:
            cursor.execute("INSERT OR IGNORE INTO flatters(id, created_at, price, url) VALUES(?,?,?,?)",
                           (apartment['id'], apartment['created_at'], apartment['price']['amount'], apartment['url']))
        con.commit()

def new_flat():
    result = []
    new = list(set(new_list()) - set(old_list()))
    for n in new:
        result.append('https://r.onliner.by/ak/apartments/' + str(n))
    return result

def send_notify():
    cursor.execute('SELECT id FROM user WHERE notify = 1')

    for row in cursor:
        user_id = row[0]
        for message in new_flat():
            bot.sendMessage(user_id, message)

def parse_subscriptions():
    updates = bot.getUpdates()

    for update in updates:
        message = update['message']
        cursor.execute("INSERT OR IGNORE INTO telegram_update(id, message) VALUES(?,?)",
                       (update['update_id'], json.dumps(update['message']),))
        user = message['from']
        cursor.execute("INSERT OR IGNORE INTO user(id, profile, notify) VALUES(?,?,?)",
                       (user['id'], json.dumps(user), 0))

        text = message['text']
        command_to_notify = {
            '/start': 1,
            '/stop': 0,
        }
        if text in command_to_notify:
            cursor.execute("UPDATE user SET notify = ? WHERE id = ?",
                           (command_to_notify[text], user['id'],))

    con.commit()


# print(old_list())
# print(new_list())
# print(new_flat())
parse_subscriptions()
send_notify()
rewrite_flatters()
