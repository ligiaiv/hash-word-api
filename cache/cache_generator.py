#!/usr/bin/env python
# -*- coding: utf-8 -*-


cache_ttl_ms = {}
"""
Time to Life of all possible requests.
Milliseconds
"""
#                     dd * hh * mm * ss * ms  
cache_ttl_ms['recent'] =        15 * 60 * 1000
cache_ttl_ms['15m'] =           15 * 60 * 1000
cache_ttl_ms['30m'] =           30 * 60 * 1000
cache_ttl_ms['1h']  =           60 * 60 * 1000
cache_ttl_ms['1h30m']  =        90 * 60 * 1000
cache_ttl_ms['6h']  =       6 * 60 * 60 * 1000
cache_ttl_ms['12h'] =       6 * 60 * 60 * 1000
cache_ttl_ms['1d']  =       6 * 60 * 60 * 1000
cache_ttl_ms['7d']  =       6 * 60 * 60 * 1000
cache_ttl_ms['15d'] =       6 * 60 * 60 * 1000

cache_dict_ms = {}
"""
Times available -> possible requests.
Milliseconds
"""
#                      dd * hh * mm * ss * ms  
cache_dict_ms['recent'] =        0
cache_dict_ms['15m'] =           15 * 60 * 1000
cache_dict_ms['30m'] =           30 * 60 * 1000
cache_dict_ms['1h']  =       1 * 60 * 60 * 1000
cache_dict_ms['1h30m']  =     1 * 90 * 60 * 1000
cache_dict_ms['6h']  =       6 * 60 * 60 * 1000
cache_dict_ms['12h'] =      12 * 60 * 60 * 1000
cache_dict_ms['1d']  =  1 * 24 * 60 * 60 * 1000
cache_dict_ms['7d']  =  7 * 24 * 60 * 60 * 1000
cache_dict_ms['15d'] = 15 * 24 * 60 * 60 * 1000


def parse_url_id(_type, FILTER, plataform):
  return str(plataform) + '/' + str(_type) + '?filter=' + str(FILTER)


def check_id_in_cache(cache, url_id, request_time):
  """
  Goes into a cache_collection and returns value if exists.
  """
  from datetime import datetime, timedelta
  from json import loads, dumps

  if request_time:
    ttl = cache_ttl_ms[request_time] #minutes
  else:
    ttl = 15 * 60 * 1000

  response = []
  query = parse_query(url_id)
  print(query)

  db_cursor = cache.find({
                'url_id': {
                '$in': [query]
                }
              })

  for doc in db_cursor:
    response = doc['data']
    created_at = doc['created_at']
    expires_after = timedelta(milliseconds=ttl)
    _id = doc['_id']

  db_cursor.close()

  if response:
    now = datetime.utcnow()

    # implement cache update when ttl expires
    if created_at + expires_after < now:
      cache.remove(_id)
      print(str(_id) + ' expired.')
      # clear response
      response = None
      response = []
    else:
      print('Found on cache.')
      print(_id)
  return response

def insert_in_cache(cache, url_id, data, request_time):
  """
  Goes into a cache_collection and inserts item.
  """
  from datetime import datetime
  from json import loads, dumps
  
  if request_time:
    ttl = cache_ttl_ms[request_time] #minutes
  else:
    ttl = 15 * 60 * 1000
  
  response = []
  query = parse_query(url_id)

  db_cursor = cache.find({
                'url_id': {
                '$in' : [query]
                }
              })

  for doc in db_cursor:
    response.append(doc['data'])

  db_cursor.close()

  if not response:
    now = datetime.utcnow()
    print(now)
    
    doc = {}
    doc['url_id'] = parse_query(url_id).pop('url_id')
    doc['data'] = data
    doc['created_at'] = now
    doc['expire_after'] = ttl

    status = cache.insert(doc, check_keys=False);

    return status
  else:
    return 'Already on cache.'


def parse_query(url_id):
  from json import loads

  split = url_id.split('?')
  plataform = split[0].split('/')[0]
  _type = split[0].split('/')[1]
  _filter = split[1].split('=')[1]

  query = {}
  query = {
    'url_id':{
    'plataform' : plataform,
    'type' : _type,
    'filter' : loads(_filter)
    }
  }

  return query
