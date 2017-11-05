# -*- coding: utf-8 -*-
from datetime import datetime

from lib_text2 import filtered, clear_text


def parse_word(collect, FILTER, projection, SKIP,LIMIT, parameters, RECENT):
  '''
  Returns list of top words plus count.
  '''
  word_count = {}

  if RECENT:
    db_cursor = collect.aggregate(parameters)

    for doc in db_cursor:
      text = doc['retweeted_status']['text']
      rt_count = doc['count']
      tmp = clear_text(text)

      # count words only once
      temp_words = []
      for word in tmp:
        if word not in temp_words:
          temp_words.append(word)
          try:
            word_count[filtered(word)] += rt_count
          except KeyError:
            word_count[filtered(word)] = rt_count
  else:
    FILTER['status.retweeted_status'] = {'$exists': False}

    db_cursor = collect.find(FILTER, projection)
    print('Tweets texts acquired: %s'% db_cursor.count())

    for doc in db_cursor:
      text = doc['status']['text']
      tmp = clear_text(text)
      temp_words = []

      # count words only once
      for word in tmp:
        if word not in temp_words:
          temp_words.append(word)
          try:
            word_count[filtered(word)] += 1
          except KeyError:
            word_count[filtered(word)] = 1
        else:

          pass

    db_cursor.close()

  top = []
  for word in word_count:
    tmp_tweets = []

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
    LIMIT = int(FILTER.get('limit', 25))
    SKIP = int(FILTER.get('skip', 0))
    RECENT = FILTER.get('recent', False)
    FILTER = FILTER['where']

    if not RECENT:
      try:
        FILTER['status.created_at']['$gte'] = datetime.strptime(FILTER['status.created_at']['gte'], '%Y-%m-%dT%H:%M:%S.%f')
        FILTER['status.created_at']['$lte'] = datetime.strptime(FILTER['status.created_at']['lte'], '%Y-%m-%dT%H:%M:%S.%f')
        FILTER['status.created_at'].pop('gte')
        FILTER['status.created_at'].pop('lte')
      except Exception as why:
        code = 400
        message = 'Invalid argument for Date: bad format or missing element.'
        raise NameError(str(why))

    try:
      FILTER['keywords']['$in'] = FILTER['categories'].pop('inq')
    except Exception:
      pass

    try:
      FILTER['keywords']['$all'] = FILTER['categories'].pop('all')
    except Exception:
      pass


    FILTER['status.retweeted_status'] = {'$exists':True}

    parameters = []
    parameters.append({'$match' : FILTER})

    if RECENT:
      parameters.append({'$limit': LIMIT})
      parameters.append({'$skip': SKIP})
    else:
      parameters.append({'$limit': 10*(LIMIT+SKIP)})

    parameters.append({
      '$group': {
        '_id': {
          'id_str': '$status.retweeted_status.id_str'
        },
        'retweeted_status': {
          '$last': '$status.retweeted_status'
        },
        'count': { '$sum': 1 }
      }
    })
    parameters.append({'$sort': { 'count': -1 }})
    parameters.append({
      '$project': {
        '_id': 0,
        'retweeted_status.text': '$retweeted_status.text',
        'count':'$count'
      }
    })

    projection = { 'status.text': 1  }
    try:
      return_dict['data'] = parse_word(collect, FILTER, projection, SKIP,LIMIT, parameters, RECENT)
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