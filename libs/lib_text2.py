#!/usr/bin/env python
# -*- coding: utf-8 -*-
import string
from lib_text import is_stopword
from lib_text import remove_latin_accents
from lib_text import is_hashtag
from lib_text import is_twitter_mention

punct = set(string.punctuation)
# adds chars not in string.punctuation
punct.add('”')
punct.add('“')
punct.add('‘')
punct.add('…')
punct.add('—')
# removes items of interest
punct.remove('#')
punct.remove('@')
punct.remove('/')
punct.remove('_')
# tab for clearing out punctuation
intab = ''.join(c for c in punct)
outtab = ''.join(' ' for c in intab)

punct_translate_tab = str.maketrans(intab, outtab)
"""
Table for removing special punctuation with translate.

"""

# Some other stopwords
word_remove_list = ['rt', '\n', '', 'http', 'https', '//t', '//', '\\']
word_start = ['@','#', 'co/', '/', '&', '\\']
word_in = ['kk', 'rsrs', '/', '\\']

# words that have commom meaning when in lowercase, but have true meaning when
# written properly, like in ptbr Sao - Saint/Sound and sao - are
dual_mean = ['ES', 'RS', 'São', 'Sao']
"""
Dual meaning words

"""

def clear_text(text):
  tmp = text.translate(punct_translate_tab)
  tmp = tmp.split()
    # splits words and checks for stopwords
  tmp2 = []
  for word in tmp:
    # clears the text from irrelevant puctuation and commom words
    if not (is_stopword(word.lower()) and word not in dual_mean) \
    and not any(w in word for w in word_in)\
    and not any((word.startswith(w) or word == w) for w in word_start) \
    and word.lower() not in word_remove_list and not isNumber(word):
      tmp2.append(word)

  return tmp2

def all_words_in_id(word_list, ids, text_dict):
  tmp = ''.join(filtered(text_word) + ' ' for text_word in text_dict[ids])
  if all(filtered(word['name']) in tmp for word in word_list):
    return True
  else:
    return False


def find_word(word_list, key):
    for word_obj in word_list:
      if filtered(word_obj['name']) == filtered(key):
        return word_obj
    return None


def filtered(str_in):
  from lib_text import remove_latin_accents
  return remove_latin_accents(str_in.lower())

def isNumber(str):
  try:
    int(str)
    return True
  except Exception:
    try:
      float(str)
      return True
    except Exception:
      return False
