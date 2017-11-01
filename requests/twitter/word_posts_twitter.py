# -*- coding: utf-8 -*-
import datetime
from operator import itemgetter

from lib_text2 import punct_translate_tab as punct_tab
from lib_text2 import filtered

def parse_post_per_word(collect, FILTER, projection, SKIP,LIMIT, parameters, RECENT):
  '''
  Returns list of tweets per word.
  '''

  word = parameters[0]['$match'].pop('word')
  output = []

  db_cursor = collect.aggregate(parameters)
  print('\nRetweets acquired.\n')

  for doc in db_cursor:
    text = doc['status']['retweeted_status']['text']

    tmp_text = filtered(text)
    tmp_text = tmp_text.translate(punct_tab)
    tmp_text = tmp_text.split(' ')

    if any(filtered(word)==filtered(w) for w in tmp_text):
      output.append(doc)

  # find for original tweets
  if len(output) < LIMIT+SKIP and not RECENT:
    FILTER['status.retweeted_status'] = {'$exists':False}

    db_cursor = collect.find(FILTER,projection)
    print('\nTweets acquired.\n')

    for doc in db_cursor:
      text = doc['status']['text']
      tmp_text = filtered(text)
      tmp_text = tmp_text.translate(punct_tab)
      tmp_text = tmp_text.split(' ')

      if any(filtered(word)==filtered(w) for w in tmp_text):
        doc['count'] = 0
        doc['status']['id'] = doc['status']['id_str']
        output.append(doc)

    db_cursor.close()


  output = sorted(output, key=itemgetter('count'), reverse=True)
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
        FILTER['status.created_at']['$gte'] = datetime.datetime.strptime(FILTER['status.created_at']['gte'], '%Y-%m-%dT%H:%M:%S.%f')
        FILTER['status.created_at']['$lte'] = datetime.datetime.strptime(FILTER['status.created_at']['lte'], '%Y-%m-%dT%H:%M:%S.%f')
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
    
    # Newly Implemented $all operator
    try:
      FILTER['keywords']['$all'] = FILTER['categories'].pop('all')
    except Exception:
      pass

    try:
      FILTER['word']
    except Exception as why:
      code = 400
      message = 'Invalid argument for Word: bad format or missing element.'
      raise NameError(str(why))

    FILTER['status.retweeted_status'] = {'$exists':True}

    parameters.append({'$match' : FILTER})
    parameters.append({
      '$group': {
        '_id': { 'id_str': '$status.retweeted_status.id_str' },
        'status': { '$last': '$status' },
        'user': { '$last': '$status.user' },
        'retweeted_status': { '$last': '$status.retweeted_status' },
        'count': { '$sum': 1 }
      }
    })
    parameters.append({'$sort': { 'count': -1 }})
    parameters.append({
      '$project': {
        '_id': '$retweeted_status.id_str',
        'status.id' : '$status.id_str',
        'status.timestamp_ms' : '$status.timestamp_ms',
        'status.user': '$user',
        'status.retweeted_status.id': '$retweeted_status.id_str',
        'status.retweeted_status.user': '$retweeted_status.user',
        'status.retweeted_status.text': '$retweeted_status.text',
        'count': '$count'
      }
    })

    if RECENT:
      parameters.append({'$limit': LIMIT})
      parameters.append({'$skip': SKIP})
    else:
      parameters.append({'$limit': 10*(LIMIT+SKIP)})
    
    projection = { 'status': 1  }
    
    try:
      return_dict['data'] = parse_post_per_word(collect, FILTER, projection, SKIP,LIMIT, parameters, RECENT)

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