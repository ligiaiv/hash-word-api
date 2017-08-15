#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

import sys

import datetime, string
from operator import itemgetter

def parse_media_project(collect, FILTER, parameters):
  output = []

  # MongoDB aggreg
  db_cursor = collect.aggregate(parameters)
  print('\nData acquired.\n')

  for doc in db_cursor:
    output.append(doc)

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
      FILTER.pop('recent')
      FILTER['where'].pop('block')
    except Exception:
      SKIP = 0


    FILTER = FILTER['where']

    try:
      if FILTER.pop('geo'):
        FILTER['data.location'] = {'$ne': None}
      else:
        FILTER['data.location'] = None
    except Exception:
      pass

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

    parameters.append({
        "$group": {
            "_id": { "id": '$data.id' },
        "data": { "$last": '$data' },
        }
        })
    parameters.append({
        "$sort": { "data.created_time": -1 }
        })
    parameters.append({
        "$skip": SKIP
        })
    parameters.append({
      "$limit": LIMIT
      })

    try:
      return_dict['data'] = parse_media_project(collect, FILTER, parameters)

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