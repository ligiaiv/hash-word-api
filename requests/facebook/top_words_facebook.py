#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

from lib_text2 import filtered, clear_text


def parse_word_face(collect, FILTER, SKIP,LIMIT, parameters, RECENT):
  word_count = {}
  top = []

  # MongoDB find
  db_cursor = collect.aggregate(parameters)
  
  print('\nPosts Acquired.\n')
  
  for doc in db_cursor:

    text = doc['message']
    if not text:
      text = ''
    tmp = clear_text(text)
    # creates a word count
    for word in tmp:
      try:
        word_count[filtered(word)] += 1
      except KeyError:
        word_count[filtered(word)] = 1

  # CREATES LIST WITH COUNT
  for word in word_count:
    top.append([word, word_count[word]])
  
  top = sorted(top, key=lambda x: x[1], reverse=True)
  top = top[SKIP:SKIP+LIMIT] # pagination implementation
  top_list = []
  
  for item in top:
    top_list.append({'word': item[0],'count': item[1]})

  return top_list

def parse_method(collect, FILTER):
  return_dict = {}
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

    parameters = []
    parameters.append({'$match': FILTER})
    parameters.append({
      '$group': {
          '_id': { '_id': '$_id' },
          'message': { '$last': '$message' },
      }
    })
    parameters.append({
      '$project': {
        '_id': 0,
        'message': '$message',
      }
    })

    if RECENT:
      parameters.append({'$limit': LIMIT})
      parameters.append({'$skip': SKIP})

    try:
      return_dict['data'] = parse_word_face(collect, FILTER, SKIP,LIMIT, parameters, RECENT)

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