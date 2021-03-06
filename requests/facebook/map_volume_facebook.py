#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

import sys, string, csv, os, json
import pymongo
import datetime
import time
from bson import json_util

# sys.path.append('./libs')
from lib_output import *
from lib_text import is_stopword
from lib_text import remove_latin_accents
from lib_text import is_hashtag
from lib_text import is_twitter_mention

from operator import itemgetter
import bottle
from bottle import route, run, template, get, request, post, response

def parse_territory_face(collect, parameters):
  control = 0
  output = []
  territory = 'territorio-'
  states = ["AC","AL","AP","AM",
      "BA","CE","DF","ES",
      "GO","MA","MT","MS",
      "MG","PA","PB","PR",
      "PE","PI","RJ","RN",
      "RS","RO","RR","SC",
      "SP","SE","TO"]

  # MongoDB aggregate
  db_cursor = collect.aggregate(parameters)
  print('\nData acquired.\n')

  # post-processing
  for item in db_cursor:
    if item['name'].startswith(territory):
      temp = item['name'].split('-')
      output.append({
        "name": temp[1].upper(),
        "count": item['count']
        })

  for state in states:
    if not any(state == s['name'] for s in output):
      control += 1 # control of zero count states
      output.append({
      "name": state,
      "count": 0
      })

  # order output
  output = sorted(output, key=itemgetter('name'))

  return output

def parse_method(collect, FILTER):
  from json import loads

  # Dictionary for returning Data
  return_dict = {}
  parameters = []

  # Default Code
  code = 200
  message = 'Done'

  try:
    # read the query input values
    # FILTER = loads(request.query.get('filter'))
    FILTER = FILTER['where']

    # implement aggregate
    # gets time
    try:
      FILTER['status.created_at']['$gte'] = datetime.datetime.strptime(FILTER['status.created_at']['gte'], '%Y-%m-%dT%H:%M:%S.%f')
      FILTER['status.created_at']['$lte'] = datetime.datetime.strptime(FILTER['status.created_at']['lte'], '%Y-%m-%dT%H:%M:%S.%f')
      FILTER['status.created_at'].pop('gte')
      FILTER['status.created_at'].pop('lte')

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

    parameters.append({
      "$match" : FILTER
      })

    parameters.append({"$unwind": '$categories'})

    parameters.append({
        "$group": {
            "_id": { "name": '$categories' },
            "count": { "$sum": 1 }
        }
        })

    parameters.append({
        "$sort": { "count": -1 }
        })

    parameters.append({
        "$project": {
          "_id": 0,
          "name": '$_id.name',
          "count": '$count'}
        })

    try:
      return_dict['data'] = parse_territory_face(collect, parameters)

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
    # json_util solves bson data_type issue
    return return_dict['data']
    