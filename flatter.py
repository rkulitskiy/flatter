import json
import telepot
import sqlite3
import configparser
import os
import requests
from datetime import datetime
import telepot


cur_dir = os.path.dirname(os.path.abspath(__file__))

config = configparser.ConfigParser()
config.read(cur_dir+'/config.ini')

con = sqlite3.connect(cur_dir+'/'+config['sqlite']['db_name'])
cursor = con.cursor()
bot = telepot.Bot(config['bot']['token'])

def task():
    array = []
    url = 'https://ak.api.onliner.by/search/apartments?order=created_at%3Adesc&metro[]=red_line&metro[]=blue_line'
    response = requests.get(url)
    resp = response.json()
    apartments = resp['apartments']
    for apartment in apartments:
        cursor.execute("SELECT id FROM flatters WHERE id = ?",
                       (apartment['id'],))
        data = cursor.fetchall()
        if len(data) == 0:
            cursor.execute("INSERT INTO flatters(id, created_at, price, url, owner, rent_type, address) "
                           "VALUES(?,?,?,?,?,?,?)",
                           (apartment['id'], apartment['created_at'],
                            apartment['price']['converted']['USD']['amount'], apartment['url'],
                            apartment['contact']['owner'], apartment['rent_type'],
                            apartment['location']['address']))
            con.commit()
            array.append([apartment['id'], apartment['price']['converted']['USD']['amount'],
                          apartment['contact']['owner'], apartment['rent_type'],
                          apartment['location']['address'], apartment['url']])
        else: break
    return array

def new_flat():
    multiplier = {
        'room': 0,
        '1_room': 1,
        '2_rooms': 2,
        '3_rooms': 3,
        '4_rooms': 4,
        '5_rooms': 5,
        '6_rooms': 6
    }
    result = []
    new = task()
    for n in new:
        result.append([n[1], n[2], multiplier[n[3]], n[4], n[5]])

    cursor.execute("INSERT INTO log(flatters, created_at) VALUES(?,?)",
                   (json.dumps(new), datetime.now().strftime("%Y-%m-%d %H:%M:%S"),))
    con.commit()

    return result

def send_notify():
    cursor.execute('SELECT id, minprice, maxprice, rooms FROM user WHERE notify = 1')
    data = cursor.fetchall()
    newFlat = new_flat()
    for row in data:
        user_id = row[0]
        minPrice = row[1]
        maxPrice = row[2]

        rooms = row[3]
        arrayRooms = []
        for r in rooms:
            if r.isdigit():
                arrayRooms.append(r)

        for list in newFlat:
            if float(list[0]) >= minPrice and float(list[0]) <= maxPrice:
                print('step1')
                for ar in arrayRooms:
                    if int(ar) == int(list[2]):
                        if list[1] == True:
                            list[1] = 'Собственник'
                        else: list[1] = 'Агент'
                        message = 'Адрес: %s' %list[3] + '\nЦена: $%s' %list[0] + '\nРазместил: %s' %list[1]+ '\nКол-во комнат: %s' %list[2] + '\n%s' %list[4]
                        bot.sendMessage(user_id, message)

send_notify()