#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""
import sys

from lib_text import remove_latin_accents

import datetime, string
from operator import itemgetter
from bottle import request

from lib_text2 import punct_translate_tab as punct_tab
from lib_text2 import filtered

def parse_post_per_word_face(collect, parameters, RECENT, LIMIT, SKIP):
  word = parameters[0]['$match'].pop('word')

  output = []

  # MongoDB find
  db_cursor = collect.aggregate(parameters)
  print('\nData acquired.\n')

  for doc in db_cursor:
    # print(doc)
    text = doc['message']
    
    if not text:
      text = ''

    tmp_text = filtered(text)
    tmp_text = tmp_text.translate(punct_tab)
    tmp_text = tmp_text.split(' ')

    if any(filtered(word)==filtered(w) for w in tmp_text):
      output.append(doc)

  output = sorted(output, key=itemgetter('like_count'), reverse=True)
  # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  output = output[SKIP:SKIP+LIMIT] # pagination implementation

  return output

def parse_method(collect, FILTER):
  # from json import loads

  # Dictionary for returning Data
  return_dict = {}
  parameters = []

  # Default Code
  code = 200
  message = 'Done'

  try:
    # read the query input values
    try:
      LIMIT = int(FILTER['limit'])
    except Exception:
      LIMIT = 25

    try:
      SKIP = int(FILTER['skip'])
    except Exception:
      SKIP = 0

    try:
      RECENT = FILTER['recent']
    except Exception:
      RECENT = False

    FILTER = FILTER['where']
    
    if not RECENT:  
      try:
        FILTER['created_time'] = {}
        FILTER['created_time']['$gte'] = datetime.datetime.strptime(FILTER['status.created_at']['gte'], '%Y-%m-%dT%H:%M:%S.%f')
        FILTER['created_time']['$lte'] = datetime.datetime.strptime(FILTER['status.created_at']['lte'], '%Y-%m-%dT%H:%M:%S.%f')

        FILTER.pop('status.created_at')
        
      except Exception as why:
        code = 400
        message = 'Invalid argument for Date: bad format or missing element.'
        raise NameError(str(why))

    try:
      FILTER['categories']['$in'] = FILTER['categories'].pop('inq')
    except Exception:
      pass
    
    # Newly Implemented $all operator
    try:
      FILTER['categories']['$all'] = FILTER['categories'].pop('all')
    except Exception:
      pass

    FILTER.pop('block')

    # sets a projection to return
    parameters = []
    parameters.append({
      "$match" : FILTER
      })

    parameters.append({
        "$sort": { "like_count": -1 }
        })

    if RECENT:
      parameters.append({
        "$limit": LIMIT
        })
      parameters.append({
          "$skip": SKIP
          })
    if not RECENT:
      parameters.append({
        "$limit": 10*(LIMIT+SKIP)
        })

    try:
      return_dict['data'] = parse_post_per_word_face(collect, parameters, RECENT, LIMIT, SKIP)

    except Exception as _why:
      print('DB Error: ' + str(_why))

  except Exception as why:
    print('Error: ' + str(why))
    code = 400
    message = 'BadRequest: ' + str(why)
  
  if code != 200:
    return_dict['meta'] = { 'code': code, 'message': message}
    return return_dict['meta']
  else:
    return return_dict['data']