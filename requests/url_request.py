# -*- coding: utf-8 -*-

def read_from_url(url):
  import urllib.request as request
  import json
  response = request.urlopen(url)
  raw = response.read()
  data = json.loads(raw.decode())

  return dumps(data, indent=4, default=json_util.default)
