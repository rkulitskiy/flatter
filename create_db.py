import sqlite3
import os
import configparser
import requests

config = configparser.ConfigParser()
config.read('config.ini')

cur_dir = os.path.dirname(os.path.abspath(__file__))
con = sqlite3.connect(cur_dir+'/'+config['sqlite']['db_name'])

with con:
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS log(id INTEGER PRIMARY KEY, dates TEXT, created_at DATE)")
    cur.execute("CREATE TABLE IF NOT EXISTS user(id INTEGER PRIMARY KEY, profile TEXT, notify INT)")
    cur.execute("CREATE TABLE IF NOT EXISTS telegram_update(id INTEGER PRIMARY KEY, message TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS flatters(id INTEGER PRIMARY KEY, created_at DATETIME, "
                "price INTEGER, url TEXT)")
    i = 1
    while i <= 21:
        url = 'https://ak.api.onliner.by/search/apartments?page=' + str(i)
        response = requests.get(url)
        resp = response.json()
        apartments = resp['apartments']
        i = i + 1

        for apartment in apartments:
            cur.execute("INSERT OR IGNORE INTO flatters(id, created_at, price, url) VALUES(?,?,?,?)",
                           (apartment['id'], apartment['created_at'], apartment['price']['amount'], apartment['url']))
        con.commit()