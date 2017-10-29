# -*- coding: utf-8 -*-

import sys

import datetime

from lib_text2 import punct_translate_tab as punct_tab
from lib_text2 import filtered

def parse_post_per_word_no_rt(collect, parameters):
  """
  Returns list of tweets per word.
  """

  word = parameters[0]['$match'].pop('word')
  output = []

  # MongoDB find
  db_cursor = collect.aggregate(parameters)
  print('\nData acquired.\n')

  for doc in db_cursor:
    text = doc['status']['text']
    tmp_text = filtered(text)
    tmp_text = tmp_text.translate(punct_tab)
    tmp_text = tmp_text.split(' ')

    if any(filtered(word)==filtered(w) for w in tmp_text):
      output.append(doc)

  return output

def parse_word_posts_no_rt(collect, FILTER):
  return_dict = {}
  parameters = []

  # Default Code
  code = 200
  message = 'Done'

  try:
    try:
      LIMIT = FILTER['limit']
    except Exception:
      LIMIT = 25

    try:
      SKIP = FILTER['skip']
    except Exception:
      SKIP = 0


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

    try:
      FILTER['word']
    except Exception as why:
      code = 400
      message = 'Invalid argument for Word: bad format or missing element.'
      raise NameError(str(why))

    FILTER['status.retweeted_status'] = {'$exists':False}

    parameters.append({
      "$match" : FILTER
      })
    parameters.append({
      "$group": {
          "_id": { "id_str": '$status.id_str' },
              "status": { "$last": '$status' },
          "count": { "$sum": 1 }
      }
    })
    parameters.append({
      "$sort": { "count": -1 }
    })
    parameters.append({
      "$project": {
        "_id": "$status.id_str",
        "status": '$status'
        }
    })
    parameters.append({
      "$limit": LIMIT
    })
    parameters.append({
      "$skip": SKIP
    })

    try:
      return_dict['data'] = parse_post_per_word_no_rt(collect, parameters)

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