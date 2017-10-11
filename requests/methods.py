# -*- coding: utf-8 -*-

METHODS = {
  'top_words' : {
    'description' : 'top_words parses the most occurent words in the database in the requested period,<br> \
            and returns a json with the list of words plus the count.<br>\
            E.g.: [<br>{ "count": 10,"word": "word1" },<br>{ "count": 5,"word": "word2" }<br>]',
    'parameters' : {
        'tags[]' : {
          'type':'vector',
          'required': False
          },
        'period' : {
          'type':'string',
          'required': True
          },
        'page' : {
          'type':'int',
          'required': True
          },
        'per_page' : {
          'type':'int',
          'required': True
          }
    },
    'plataforms' : {
        'twitter':{
              'path' : 'top_words_twitter'
              },
        'facebook':{
              'path' : 'top_words_facebook'
              },
        'facebook_comments':{
              'path' : 'top_words_facebook_comments'
              }
        }
  },

  'word_posts' : {
    'description' : 'Given one word, it returns the interactions in the database,<br> \
            with it. Return is a json with the list of interactions found.<br>\
            E.g.: [<br>{ POST1 },<br>{ POST2 }<br>]',
    'parameters' : {
        'tags[]' : {
          'type':'vector',
          'required': False
          },
        'period' : {
          'type':'string',
          'required': True
          },
        'page' : {
          'type':'int',
          'required': True
          },
        'per_page' : {
          'type':'int',
          'required': True
          },
        'word' : {
          'type' : 'string',
          'required' : True
        }
    },
    'plataforms' : {
        'twitter':{
              'path' : 'word_posts_twitter'
              },
        'facebook':{
              'path' : 'word_posts_facebook'
              },
        'facebook_comments':{
              'path' : 'word_posts_facebook_comments'
              }
        }
  },

  'word_images' : {
    'description' : 'Given one word, it returns the interactions with images in the database,<br> \
            with it. Return is a json with the list of interactions found.<br>\
            E.g.: [<br>{ POST_IMG_1 },<br>{ POST_IMG_2 }<br>]',
    'parameters' : {
        'tags[]' : {
          'type':'vector',
          'required': False
          },
        'period' : {
          'type':'string',
          'required': True
          },
        'page' : {
          'type':'int',
          'required': True
          },
        'per_page' : {
          'type':'int',
          'required': True
          },
        'word' : {
          'type' : 'string',
          'required' : True
        }
    },
    'plataforms' : {
        'twitter':{
              'path' : 'word_images_twitter'
              },
        'facebook':{
              'path' : 'word_images_facebook'
              },
        'facebook_comments':{
              'path' : 'word_images_facebook_comments'
              }
        }
  },

  'map_volume' : {
    'description' : 'Returns the volume of interactions in the database in the given period,<br> \
            by state. Return is a json with the list of states and the volume found.<br>\
            E.g.: [<br>{"name": "STATE1","count": 100},<br>{"name": "STATE2","count": 700}<br>]',
    'parameters' : {
        'tags[]' : {
          'type':'vector',
          'required': False
          },
        'period' : {
          'type':'string',
          'required': True
          },
        'page' : {
          'type':'int',
          'required': True
          },
        'per_page' : {
          'type':'int',
          'required': True
          }
    },
    'plataforms' : {
        'twitter':{
              'path' : 'map_volume_twitter'
              },
        'facebook':{
              'path' : 'map_volume_facebook'
              },
        'facebook_comments':{
              'path' : 'map_volume_facebook_comments'
              }
        }
  },

  'media' : {
    'description' : 'Returns the N most recent interactions in the database, based on the limit requested.<br> \
            Return is a json with the list of interactions found.<br>\
            E.g.: [<br>{ POST_IMG_1 },<br>{ POST_IMG_2 }<br>]',
    'parameters' : {
        'tags[]' : {
          'type':'vector',
          'required': False
          },
        'period' : {
          'type':'string',
          'required': True
          },
        'page' : {
          'type':'int',
          'required': True
          },
        'per_page' : {
          'type':'int',
          'required': True
          },
        'geo' : {
          'type':'boolean',
          'required': False
          }
    },
    'plataforms' : {
        'instagram':{
          'path': 'media_instagram'
        }
    }
  }
}
