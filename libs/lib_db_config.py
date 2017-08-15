#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pymongo
from pymongo import MongoClient

def read_db_config(folder, filename):
  return {
    'user': os.environ['MONGO_URI_USER'],
    'password': os.environ['MONGO_URI_PASSWORD'],
    'server': os.environ['MONGO_URI_SERVER'],
    'port': os.environ['MONGO_URI_PORT'],
    'db': os.environ['MONGO_URI_DB'],
    'twitter': os.environ['COLLECTION_TWITTER'],
    'facebook_comments': os.environ['COLLECTION_FB_COMMENTS'],
    'facebook_pages': os.environ['COLLECTION_FB_PAGES'],
    'facebook_posts': os.environ['COLLECTION_FB_POSTS'],
    'instagram': os.environ['COLLECTION_INSTAGRAM'],
    'cache': os.environ['COLLECTION_CACHE'],
  }

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