#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import datetime
from json import loads, dumps

from bottle import request

# import requests available and plataforms folders per method
sys.path.append('./requests')
from methods import METHODS
for method in METHODS:
  for plataform in METHODS[method]['plataforms']:
    path = './requests/' + plataform
    if path not in sys.path:
      sys.path.append(path)
      print('Appending to sys.path: ' + path)
# cache
sys.path.append('./cache')
from cache_generator import parse_url_id, check_id_in_cache, cache_dict_ms, insert_in_cache

def parse_filter_cache(method, cache, _filter='', plataform=''):
  _delta = None
  FILTER = {}
  # remove blocked posts
  # FILTER['where']['block'] = False

  if not _filter:
    try:
      _filter = request.query.decode().get('filter')
      FILTER = loads(_filter)
    except Exception:
      required_missing = []
      parameters = METHODS[method]['parameters'].copy()
      print('parameters %s'%parameters)

      for param in parameters:
        query_parameter = request.query.decode().getall(param)

        if not query_parameter and parameters[param]['required']:
          required_missing.append(param)
        else:
          if parameters[param]['type'] == 'int':
            parameters[param] = int(query_parameter[0])

          elif parameters[param]['type'] == 'string':
            parameters[param] = query_parameter[0]

          elif parameters[param]['type'] == 'vector':
            parameters[param] = query_parameter

          elif parameters[param]['type'] == 'boolean':
            if query_parameter:
              parameters[param] = (query_parameter[0] == 'true')

      if required_missing:
        raise NameError('Parameters Missing: ' + str(required_missing))

      # parse input

      try:
        FILTER['where'] = {}
        FILTER['where']['period'] = parameters['period']
        if parameters.get('tags[]'):
          FILTER['where']['keywords'] = { '$all': parameters['tags[]'] }
        if parameters.get('page') and parameters.get('per_page'):
          FILTER['limit'] = parameters['per_page']
          FILTER['skip'] = parameters['per_page']*(parameters['page'] - 1)
        if parameters.get('word'):
          FILTER['where']['word'] = parameters['word']
        if parameters.get('geo') is not None:
          FILTER['where']['geo'] = parameters['geo']

      except Exception as why:
        print(why)
        pass

      _filter = dumps(FILTER)

  try:
    lte = datetime.datetime.strptime(FILTER['where']['status.created_at']['lte'], '%Y-%m-%dT%H:%M:%S.%f')
    gte = datetime.datetime.strptime(FILTER['where']['status.created_at']['gte'], '%Y-%m-%dT%H:%M:%S.%f')
  except Exception as why:
    lte = datetime.datetime.now()
    try:
      _delta = FILTER['where'].pop('period')
      if _delta not in cache_dict_ms:
        raise NameError('Wrong timing.')
      # +++++++++++++++++++++++++++++++++++++++++++++++++++
      # recent

      if not _delta == 'recent':
        delta = cache_dict_ms[_delta]
        gte = lte - datetime.timedelta(milliseconds=delta)
        FILTER['where']['status.created_at'] = {}
        FILTER['where']['status.created_at']['lte'] = lte.strftime('%Y-%m-%dT%H:%M:%S.%f')
        FILTER['where']['status.created_at']['gte'] = gte.strftime('%Y-%m-%dT%H:%M:%S.%f')
      else:
        FILTER['recent'] = True

    except Exception:
      raise NameError('Missing or wrong interval.')


  _id_ = parse_url_id(method, _filter, plataform)

  in_cache = None
  in_cache = check_id_in_cache(cache, _id_, _delta)

  if in_cache:
    FILTER['data'] = in_cache
    FILTER['found_on_cache']=True

  FILTER['id'] = _id_
  FILTER['period'] = _delta

  print('FITLER:\n%s'%FILTER)
  # _filter is ready
  return FILTER


def word_api_request(_url_ = '', db=None, method='', plataform=''):
  """
  For request parameters. Gets the type of request and returns the correct response.
  """
  response = None

  # when a url is sent, it is a request from the cache generator
  # otherwise get parameters globally
  if not _url_:
    FILTER = parse_filter_cache(method, db['cache'], plataform=plataform)

  else:
    _split_url =_url_.split('=')
    _filter = _split_url[1]
    FILTER = parse_filter_cache(method, db['cache'], _filter=_filter)

  _url_id = FILTER.pop('id')
  _period = FILTER.pop('period')

  # returns if found on cache
  try:
    FILTER['found_on_cache']
    response = FILTER['data']
    cached = True

  except Exception:
    cached = False
    # not in cache, so process it and inserts in cache

    class_method = __import__ (METHODS[method]['plataforms'][plataform]['path'])
    parse_method = getattr(class_method, 'parse_method')

    if(plataform=='twitter'):
      response = parse_method(db['twitter'], FILTER)
    elif(plataform=='facebook'):
      response = parse_method(db['facebook_pages'], FILTER)
    elif(plataform=='facebook_comments'):
      response = parse_method(db['facebook_comments'], FILTER)
    elif(plataform=='instagram'):
      response = parse_method(db['instagram'], FILTER)

  if not response:
    return []
  elif not cached:
    try:
      # not empty and not cached, some error might have happenned
      print(response['message'])
    except Exception:
      status = ''
      status = insert_in_cache(db['cache'], _url_id, response, _period)
      print('Inserted on Cache: \n' + str(status))

  return response