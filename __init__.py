#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

import sys, string, csv, os, json
import pymongo
import datetime
import time
from json import dumps

from bson import json_util
from word_api import word_api_request

sys.path.append('./libs')
from lib_db_config import read_db_config, db_connect

sys.path.append('./requests')
from methods import METHODS

import bottle
from bottle import route, run, response

#Global Variables
runtime = datetime.datetime.now()
log = 'time_stream_' + runtime.strftime("%d-%m-%Y %H:%M:%S") + '.log'
log_folder = 'logs'

Mongodb = ''
SERVER = ''
PORT = ''
DB = ''
COLLECT = {}
CACHE = ''
INTERVAL = ''
USER = ''
PASSWD = ''

def get_about():
  header = 'WORD API'
  by = 'Labic 2015 UFES<br>Vitória-ES Brasil'
  about_page = '<html><body><h1>'+ header +'</h1><br>by:'+ by +'<br><br><b>METHODS:</b><br><br>'
  methods = []
  for method in METHODS:
    methods.append(method)
  methods.sort()
  for method in methods:
    
    description = METHODS[method].get('description')
    
    plataforms = []
    for plataform in METHODS[method].get('plataforms'):
      plataforms.append(plataform)

    plataforms.sort()
  
    plataform_txt = ''
    for plataform in plataforms:
      plataform_txt = plataform_txt + '- ' + plataform + '<br>'

    parameters = str(METHODS[method]['parameters'])

    about_response = str(method).upper() + '<br>Plataforms:<br>' + str(plataform_txt) + '<br>Description:<br>' + str(description) + '<br>' + '<br>Parameters:<br>' + str(parameters) + '<br><br>'
    about_page = about_page + about_response
  
  about_page = about_page + '</body></html>'

  return about_page

# the decorator
def enable_cors(fn):
    def _enable_cors(*args, **kwargs):
        # set CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
        response.headers['Content-type'] = 'application/json; charset=utf-8'
 
        if bottle.request.method != 'OPTIONS':
            # actual request; reply with the actual response
            return fn(*args, **kwargs)
 
    return _enable_cors

# ========================================================================================================================
def setup_db():
  # Main part of the program
  # Configures necessary things and sets some variables
  global SERVER, PORT, DB, COLLECT, CACHE, INTERVAL, USER, PASSWD

  DATA = read_db_config('config', 'db_init.py')
  
  try:
    SERVER = DATA['server']
    PORT = DATA['port']
    DB = DATA['db']
    COLLECT['twitter'] = DATA['twitter']
    COLLECT['facebook_comments'] = DATA['facebook_comments']
    COLLECT['facebook_pages'] = DATA['facebook_pages']
    COLLECT['facebook_posts'] = DATA['facebook_posts']
    COLLECT['instagram'] = DATA['instagram']
    CACHE = DATA['cache']

  except Exception as e:
    text = "ERROR: Your config file is missing or wrong!\nCheck for the ./.config/.db_init.\nAborting...\n" + str(e)
    print(text)
    write_log(log_folder, log, text)
    exit()

  try:
    USER = DATA['user']
    PASSWD = DATA['password']
  except KeyError:
    USER = ''
    PASSWD = ''
  global Mongodb
  Mongodb = db_connect(SERVER, PORT, DB, COLLECT, CACHE, USER, PASSWD)

# Route for parsing the requests with the given filter
@route('/<plataform>/<method>')
@enable_cors
def parsed(plataform, method):
  if method not in METHODS:
    return 'Method ' + method + ' nonexistent.'
  if plataform not in METHODS[method]['plataforms']:
    return 'Method ' + method + ' does not support ' + plataform + '.'

  try:
    response = word_api_request(plataform=plataform, method=method, db=Mongodb)
    return dumps(response, indent=4, default=json_util.default)
  except Exception as why:
    return dumps('Request caused an Error: ' + str(why))

@route('/<about>')
def parsed(about):
  print('Request: /' + about)
  return about_page

@route('/')
def parsed():
  print('Request: /')
  return about_page

# =======================================================================
if __name__ == "__main__":
  setup_db()
  about_page = get_about()
  try:
    port = sys.argv[1]
    print('port: ' + str(port))
  except Exception:
    port = os.environ.get('PORT', 8081)
    print('Default port: ' + str(port))
  # starts server
  # multithread CherryPy
  run(host='0.0.0.0', port=port, server='cherrypy')