#!/usr/bin/env python
import os
import re
import logging
import yaml
import base64
import urllib
import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.api import urlfetch
from google.appengine.ext.webapp.util import run_wsgi_app

class Hatebu2DeliciousHandler(webapp.RequestHandler):
  def post(self):
    if (self.request.get('status') == 'add' or self.request.get('status') == 'update') :
      delicious = Delicious(
        username=self.request.get('username'),
        title=self.request.get('title'),
        url=self.request.get('url'),
        description=self.request.get('comment'),
        tags=self.__extract_tags(self.request.get('comment'))
      )
      delicious.post()

  def __extract_tags(self, comment):
    tag_pattern = re.compile("\[([^\:\[\]]+)\]", re.I)
    tags = tag_pattern.findall(comment)
    return tags

class Delicious(object):
  def __init__(self, username, title, url, description, tags):
    self.username = username
    self.title = title
    self.url = url
    self.description = description
    self.tags = tags
    config = self.load_config()
    self.user = config['delicious_user']
    self.password = config['delicious_pass']
    return

  def load_config(self):
    config = yaml.safe_load(open(os.path.join(os.path.dirname(__file__), 'config.yaml'), 'r'))
    return config

  def post(self):
    try:
      auth = base64.b64encode('%s:%s' % (self.user, self.password)).strip("\n")
      res = urlfetch.fetch(self.endpoint_uri(), headers={ 'Authorization' : 'Basic %s' % auth }).status_code

    except Exception, e:
      logging.error(e)
      pass

  def endpoint_uri(self):
    logging.info(self.title)
    endpoit_uri = 'https://api.del.icio.us/v1/posts/add?' + urllib.urlencode({ 
      'url' : self.url, 
      'description' : self.title.encode('utf-8'), 
      'extended' : self.description, 
      'tags' : ' '.join(self.tags)
    })
    return endpoit_uri

def main():
  application = webapp.WSGIApplication([('/', Hatebu2DeliciousHandler)], debug=True)
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
