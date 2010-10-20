from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from django.utils import simplejson as json

import urllib


class RequestHandler(webapp.RequestHandler):
  def write(self, data):
    self.response.out.write(data)

  def render(self, path, params):
    self.write(template.render(path, params))

  def inspect(self, obj):
    self.write(repr(obj))

  def json(self, data):
    self.response.headers.add_header('Content-Type', 'application/json')

    self.write(json.dumps(data))

  def mturk_submit_url(self):
    host_url = self.request.get('turkSubmitTo', 'https://www.mturk.com')

    params = {'assignmentId': self.worker.assignment_id, 'workerId': self.worker.id}

    return '%s/mturk/externalSubmit?%s' % (host_url, urllib.urlencode(params))

  def host_url(self, path):
    return '%s%s?%s' % (self.request.host_url, path, self.request.query_string)

  def bad_request(self, text='Bad Request'):
    self.response.set_status(400)

    self.write(text)

  def not_found(self, text='Not Found'):
    self.response.set_status(404)

    self.write(text)

  def internal_server_error(self, text='Internal Server Error'):
    self.response.set_status(500)

    self.write(text)