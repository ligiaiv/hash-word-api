#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

import sys, string, csv, os, json

def get_posts_from_list(collect, FILTER, projection):
  """
Returns posts from a list of ids.
  """
  return_list = []

  # MongoDB find
  db_cursor = collect.find(FILTER, projection)
  # puts results in a list
  if db_cursor:
    for doc in db_cursor:
      return_list.append(doc)

  return return_list

def get_posts(collect, FILTER):
  from json import dumps
  # from bottle import request

  # Dictionary for returning Data
  return_dict = {}

  # Default Code
  code = 200
  message = 'Done'

  try:
    # read the query input values
    # FILTER = loads(request.query.get('filter'))
    FILTER = FILTER['where']

    id_list = FILTER.pop('id_list')
    # print(id_list)

    _id_list = []
    for _id in id_list:
      if _id.startswith('I'):
        _id_list.append(_id.split('I')[1])
      else:
        _id_list.append(_id)

    # implemented return tweets with imgs

    # print(_id_list)
    FILTER['status.id_str'] = { '$in' : _id_list }

    # sets a projection to return
    projection = { 'status': 1, '_id': 0 }

    try:
      print(FILTER)
      return_dict['data'] = get_posts_from_list(collect, FILTER, projection)

    except Exception as _why:
      print('DB Error: ' + str(_why))
      code = 408
      message = 'RequestTimeout'

  except Exception as why:
    print('Error: ' + str(why))
    code = 400
    message = 'BadRequest: ' + str(why)
  
  if code != 200:
    return_dict['meta'] = { 'code': code, 'message': message}
    return return_dict['meta']
  else:
    return return_dict['data']