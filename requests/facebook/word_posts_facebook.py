#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from operator import itemgetter

from lib_text2 import punct_translate_tab as punct_tab
from lib_text2 import filtered


def parse_post_per_word_face(collect, parameters, RECENT, LIMIT, SKIP):
  word = parameters[0]['$match'].pop('word')
  output = []

  db_cursor = collect.aggregate(parameters)

  for doc in db_cursor:
    text = doc['message']
    
    if not text:
      text = ''

    tmp_text = filtered(text)
    tmp_text = tmp_text.translate(punct_tab)
    tmp_text = tmp_text.split(' ')

    if any(filtered(word)==filtered(w) for w in tmp_text):
      output.append(doc)

  output = sorted(output, key=itemgetter('likes_count'), reverse=True)
  output = output[SKIP:SKIP+LIMIT] # pagination implementation

  return output


def parse_method(collect, FILTER):
  return_dict = {}
  parameters = []
  code = 200
  message = 'Done'

  try:
    LIMIT = int(FILTER.get('limit', 25))
    SKIP = int(FILTER.get('skip', 0))
    RECENT = FILTER.get('recent', False)
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
    
    try:
      FILTER['categories']['$all'] = FILTER['categories'].pop('all')
    except Exception:
      pass

    # FILTER.pop('block')

    parameters = []
    parameters.append({'$match' : FILTER})
    parameters.append({'$sort': { 'likes_count': -1 }})

    if RECENT:
      parameters.append({'$limit': LIMIT})
      parameters.append({'$skip': SKIP})
    else:
      parameters.append({'$limit': 10*(LIMIT+SKIP)})

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