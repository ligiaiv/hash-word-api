#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pymongo
from pymongo import MongoClient

#mongo config
SERVER = ''
PORT = ''
USER = ''
PASSWD = ''
DB = ''
COLLECT = ''
CACHE = ''

def read_db_config(folder, filename):
  with open(os.path.join(folder, filename), 'r') as db_init:
    DATA = {}
    for line in db_init:
      if line.startswith('#') or line == '\n':
        continue
      else:
        data = line
        data = data.split(' ')
        for i in range(0,len(data),2):
          # remove line break at the enddings
          if data[i+1].endswith('\n'):
            data[i+1] = data[i+1][:(len(data[i+1])-1)]
          # append to config data
          DATA[data[i]] = data[i+1]

    return DATA

def db_connect(SERVER, PORT, DB, COLLECT, CACHE, USER, PASSWD):
  print('\nTrying to connect to ' + SERVER + ' at ' + PORT)
  db = {}

  try:
    client = MongoClient(SERVER, int(PORT)) #recommended after 2.6
    database = client[DB]
    if USER and PASSWD:
      try:
        database.authenticate(USER, PASSWD)
        print('### Authenticated ####')
      except Exception as why:
        print('Authentication Failed!!!')
        print(why)

    for collection in COLLECT:
      db[collection] = database[COLLECT[collection]]

    # ++++++++++++++++++++++++++++++++++++++++++
    db['cache'] = database[CACHE]
    db['client'] = client

  except Exception as why:
    print('Something went wrong.\n')
    print(why)
    exit()


  print('\nConnection to ' + SERVER + ' was succesfull!')

  return db