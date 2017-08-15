#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, string, csv, os, json
import pymongo
import datetime
import time
from bson import json_util

sys.path.append('./libs')
from lib_db_config import read_db_config, db_connect
from lib_output import *

# cache
sys.path.append('./cache')
from cache_generator import parse_url_id, check_id_in_cache, insert_in_cache

#Global Variables
runtime = datetime.datetime.now()
log = 'time_stream_' + runtime.strftime("%d-%m-%Y %H:%M:%S") + '.log'
log_folder = 'logs'

# ========================================================================================================================
def setup_db_connection():
  # Main part of the program
  # Configures necessary things and sets some variables
  global SERVER, PORT, DB, COLLECT, CACHE, INTERVAL, USER, PASSWD

  DATA = read_db_config('config', 'db_init.py')

  try:
    SERVER = DATA['server']
    PORT = DATA['port']
    DB = DATA['db']
    COLLECT = DATA['collection']
    CACHE = DATA['cache']

  except Exception as e:
    text = "ERROR: Your config file is missing or wrong!\nCheck for the ./.config/.idb_init.\nAborting...\n"
    print(text)
    write_log(log_folder, log, text)
    exit()

  try:
    USER = DATA['user']
    PASSWD = DATA['password']
  except KeyError:
    USER = ''
    PASSWD = ''

  db = db_connect(SERVER, PORT, DB, COLLECT, CACHE, USER, PASSWD)
  
  return db

def find_time_partition(now):
  """
  15 minutes time partitions
  """
  fixed_hour = datetime.datetime(year=now.year, month=now.month, day=now.day, hour=now.hour-1, minute=45)
  fixed_hour_15 = datetime.datetime(year=now.year, month=now.month, day=now.day, hour=now.hour, minute=15)
  fixed_hour_30 = datetime.datetime(year=now.year, month=now.month, day=now.day, hour=now.hour, minute=30)
  fixed_hour_45 = datetime.datetime(year=now.year, month=now.month, day=now.day, hour=now.hour, minute=45)
  
  if now < fixed_hour_15:
    return fixed_hour
  elif now < fixed_hour_30:
    return fixed_hour_15
  elif now < fixed_hour_45:
    return fixed_hour_30
  else:
    return fixed_hour_45

def format_date(date):
  return date.strftime('%Y-%m-%dT%H:%M:%S.0')


def parse_filter(_type_, interval, theme=None, categories=None, quantity=None):
  """
  creates a filter partitioning the time lapse for the cache.
  """
  import datetime
  import time
  
  _filter_ =   ""
  
  now = datetime.datetime.now()
  delta = datetime.timedelta(minutes=interval)
  lte = find_time_partition(now)
  gte = lte - datetime.timedelta(minutes=interval)


  _filter_ = _filter_ + "{\"where\":{\"status.created_at\":{\"gte\":"
  # lower time 2015-10-10T00:00:00.0
  _filter_ = _filter_ + "\"" + format_date(gte) + "\""
  _filter_ = _filter_ + ",\"lte\":"
  # upper time 2015-10-10T00:15:00.0
  _filter_ = _filter_ + "\"" + format_date(lte) + "\""
  _filter_ = _filter_ + "}"
  # theme
  if theme:
    _filter_ = _filter_ + ",\"theme\":\"" + theme + "\""
  if categories:
    _filter_ = _filter_ + ",\"categories\":{\"all\":" + "[\"" + categories + "\"]}"
  
  _filter_ = _filter_ + "}}"

  return _filter_

def process(db, args):
  # implement requests
  from json import dumps
  from word_api import word_api_request

  arguments = {}
  for arg in args:
    tmp = arg.split('=')
    try:
      arguments[tmp[0]] = tmp[1]
    except Exception:
      pass

  _interval = None
  _theme = None
  _categories = None
  _quantity = None

  try:
    _interval = int(args[2])
  except Exception:
    pass
  try:
    _theme = arguments['-t']
  except Exception:
    pass
  try:
    _categories = arguments['-c']
  except Exception:
    pass
  try:
    _quantity = arguments['-q']
  except Exception:
    pass
  
  if args[1] == '--find_one':
    print('find_one: ')
    print(db['cache'].find_one())

  if args[1] == '--top_words':
    if not _interval:
      return 'Interval missing.'
    else:
      _filter_ = parse_filter('top_words', _interval, theme=_theme, categories=_categories, quantity=_quantity)

    _url_id = parse_url_id('top_words', _filter_)

    data = word_api_request(_url_=_url_id, db=db, _type_='top_words')
    
    if not 'Error' in data:
      print('Processed id: ' + _url_id)
    else:
      if 'Error' in data:
        print(data)

  else:
    return '\nNo equivalent request found for ' + str(args[1])

# =======================================================================
if __name__ == "__main__":
  if(sys.argv[1] in ['--help', '-h']):
    print('\nUSAGE:\n')
    print('python3 cache_requests type interval -t=theme -c=categories -q=quantity\n')
  else:
    db = setup_db_connection()
    process(db, sys.argv)
    print('\nClosing connection...')
    db['client'].close()