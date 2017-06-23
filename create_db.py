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
    cur.execute("CREATE TABLE IF NOT EXISTS log(id INTEGER PRIMARY KEY, flatters TEXT, created_at DATE)")
    cur.execute("CREATE TABLE IF NOT EXISTS user(id INTEGER PRIMARY KEY, profile TEXT, notify INT)")
    cur.execute("CREATE TABLE IF NOT EXISTS telegram_update(id INTEGER PRIMARY KEY, message TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS flatters(id INTEGER PRIMARY KEY, created_at DATETIME, "
                "price INTEGER, url TEXT, owner BOOLEAN, rent_type TEXT, address TEXT)")
    i = 1
    while i <= 21:
        url = 'https://ak.api.onliner.by/search/apartments?order=created_at%3Adesc&page=' + str(i)
        response = requests.get(url)
        resp = response.json()
        apartments = resp['apartments']
        i = i + 1

        for apartment in apartments:
            cur.execute("INSERT INTO flatters(id, created_at, price, url, owner, rent_type, address) "
                           "VALUES(?,?,?,?,?,?,?)",
                           (apartment['id'], apartment['created_at'],
                            apartment['price']['converted']['USD']['amount'], apartment['url'],
                            apartment['contact']['owner'], apartment['rent_type'],
                            apartment['location']['address']))
        con.commit()