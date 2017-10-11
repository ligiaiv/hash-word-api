# -*- coding: utf-8 -*-

"""
"""

import sys, string, csv, os, json

import re

import pymongo
import datetime
from bson import json_util

from lib_text import is_stopword
from lib_text import remove_latin_accents
from lib_text import is_hashtag
from lib_text import is_twitter_mention
from lib_text2 import punct_translate_tab as punct_tab
from lib_text2 import dual_mean, filtered, isNumber, word_remove_list, word_start, word_in, clear_text

def read_from_url(url):
  import urllib.request as request
  import json
  response = request.urlopen(url)
  raw = response.read()
  data = json.loads(raw.decode())

  return dumps(data, indent=4, default=json_util.default)

def parse_word(collect, FILTER, projection, SKIP,LIMIT, parameters, RECENT):
  """
Returns list of top words plus count.
  """
  word_count = {}
  top = []

  # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  db_cursor = collect.aggregate(parameters)

  print('Retweets texts acquired')
  
  for doc in db_cursor:
    text = doc['retweeted_status']['text']
    rt_count = doc['count']

    tmp = clear_text(text)

    # creates a word count
    temp_words = []
    for word in tmp:
      if word not in temp_words:
        temp_words.append(word)
        try:
          word_count[filtered(word)] += rt_count
      
        except KeyError:
          word_count[filtered(word)] = rt_count
      else:
        # count words only once
        pass

  if not RECENT:
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # MongoDB find
    FILTER['status.retweeted_status'] = {'$exists':False}

    db_cursor = collect.find(FILTER, projection)
    print('Tweets texts acquired: %s'% db_cursor.count())
    
    for doc in db_cursor:
      text = doc['status']['text']

      tmp = clear_text(text)

      temp_words = []
      for word in tmp:
        if word not in temp_words:
          temp_words.append(word)
          try:
            word_count[filtered(word)] += 1
        
          except KeyError:
            word_count[filtered(word)] = 1
        else:
          # count words only once
          pass

    db_cursor.close()

  # CREATES LIST WITH COUNT
  for word in word_count:
    tmp_tweets = []

    top.append([word, word_count[word]])
  
  top = sorted(top, key=lambda x: x[1], reverse=True)
  # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  top = top[SKIP:SKIP+LIMIT] # pagination implementation
  
  top_list = []
  
  for item in top:
    top_list.append({'word': item[0],'count': item[1]})

  return top_list

def parse_method(collect, FILTER):
  from json import dumps, loads

  # Dictionary for returning Data
  return_dict = {}

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
      RECENT = FILTER['recent']
    except Exception:
      RECENT = False

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
    
    try:
      FILTER['keywords']['$all'] = FILTER['categories'].pop('all')
    except Exception:
      pass

    # sets a projection to return
    projection = { 'status.text': 1  }

    FILTER['status.retweeted_status'] = {'$exists':True}

    parameters = []
    parameters.append({
      "$match" : FILTER
      })
    if RECENT:
      parameters.append({
        "$limit": LIMIT
        })
      parameters.append({
          "$skip": SKIP
          })

    parameters.append({
        "$group": {
            "_id": { "id_str": '$status.retweeted_status.id_str' },
                "retweeted_status": { "$last": '$status.retweeted_status' },
            "count": { "$sum": 1 }
        }
        })
    parameters.append({
        "$sort": { "count": -1 }
        })

    parameters.append({
        "$project": {
          "_id": 0,
          "retweeted_status.text": '$retweeted_status.text',
          "count":"$count"
          }
        })

         
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
    # json_util solves bson data_type issue
    return return_dict['data']