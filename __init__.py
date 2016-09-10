from constants import *
from flask import Flask, jsonify
import names
import pycurl
import uuid
import urllib2

app = Flask(__name__)

@app.route("/")
def index():
  return jsonify(**{'message': "200 OK!"})

@app.route("/verify/<path:url>")
def verify(url):
  url = _parse_url(url)
  if url is None:
    return 'False'
  else:
    return str(accepts_range(url))

@app.route("/partition/<path:url>/<int:n>")
def partition(url, n):
  url = _parse_url
  if url is not None and accepts_range(url):
    size = get_file_size(url)
    resp = {
      '_id': names.get_full_name().replace(' ', ''),
      'ranges': [],
      'size': size
    }
    if size < n:
      for i in xrange(0, size+1, 2):
        if i == size:
          resp['ranges'].append(_stringify(str(i), ''))
        else:
          resp['ranges'].append(_stringify(str(i), str(i+1)))
      rem = n - len(resp['ranges'])
    else:
      step_size = int(size) / n
      start = 0
      stop = -1
      for i in xrange(n):
        start = stop + 1
        stop += step_size
        if (i == n-1):
          resp['ranges'].append(_stringify(str(start), ''))
        else:
          resp['ranges'].append(_stringify(str(start), str(stop)))
    return jsonify(**resp)
  else:
    return jsonify(**{'error': 'URL not valid'}) 

def _parse_url(url):
  if url.startswith('https'):
    url = 'https://' + url[7:]
  elif url.startswith('http'):
    url = 'http://' + url[6:]
  else:
    return None

def _stringify(i, j):
  return 'bytes=' + i + '-' + j

def get_file_size(url):
  return urllib2.urlopen(url).info()['Content-Length']

def accepts_range(url):
  header = urllib2.urlopen(url).info()
  for key in header:
    if key in RANGE_HEADERS:
      if header[key] in VALID_OPTIONS:
        return True
      else:
        return False
  return fallback_check(url)

def fallback_check(url): # actually construct a HEAD request and check for 206
  c = pycurl.Curl()
  c.setopt(c.RANGE, '0-0') # First byte
  c.setopt(c.URL, url)
  c.setopt(c.NOBODY, 1)
  c.perform()

  http_code = c.getinfo(c.HTTP_CODE)
  c.close()

  if http_code == 206:
    return True
  else:
    return False

if __name__ == "__main__":
  app.run()
