from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app as run_wsgi
from google.appengine.api import urlfetch

from hagglebot.http import RequestHandler
from hagglebot.models import *
from hagglebot.util import *
from hagglebot.views import ConfirmView
from hagglebot import hagglorithm, mturk

import time, random, yaml, logging


class Root(RequestHandler):
  def get(self):
    self.write('OK')


class Upload(RequestHandler):
  def get(self):
    self.render('priv/upload.html', {'action': self.request.url})

  def post(self):
    data = yaml.load(self.request.get('file'))

    experiment = Experiment()

    for (k, v) in data.iteritems():
      if k != 't2_groups':
        setattr(experiment, k, v)

    experiment.group_count = len(data['t2_groups'])
    experiment.group_index = 0
    experiment.put()

    for group_data in data['t2_groups']:
      group = Group()

      for (k, v) in group_data.iteritems():
        setattr(group, k, v)

      group.experiment = experiment
      group.put()

    location = '%s/confirm?key=%s' % (self.request.host_url, experiment.key())

    self.redirect(location)


class Confirm(RequestHandler):
  @experiment_required
  def get(self):
    groups = Group.all().filter('experiment = ', self.experiment)

    self.render('priv/confirm.html', {
      'view': ConfirmView(self.experiment, list(groups))
    , 'action': self.request.url
    })

  @experiment_required
  def post(self):
    url = '%s/task/1?key=%s' % (self.request.host_url, self.experiment.key())

    response = mturk.create_hit(url, self.experiment)

    if response.status is True:
      self.experiment.hit_id = response[0].HITId
      self.experiment.put()

      self.response.set_status(201)

      self.write('Created HITId=' + response[0].HITId)
    else:
      logging.error('could not create hit for experiment %s (%s)' % (self.experiment.key(), response.reason))

      self.response.set_status(500)

      self.write('Bad mturk response')


class Task1(RequestHandler):
  @experiment_required
  def get(self):
    # TODO: validate assignmentId?

    assignment_id = self.request.get('assignmentId', None)

    if assignment_id is None:
      self.not_found()
    elif assignment_id == 'ASSIGNMENT_ID_NOT_AVAILABLE':
      self.render('priv/preview.html', {'experiment': self.experiment})
    else:
      worker_id = self.request.get('workerId')

      worker = worker_lookup(worker_id, assignment_id)

      if worker is None:
        worker = Worker()
        worker.id = worker_id
        worker.assignment_id = assignment_id
        worker.group = next_group(self.experiment)
        worker.put()

      self.render('priv/task_1.html', {
        'image': self.experiment.t1_image_url
      , 'action': self.request.url
      })

  @experiment_required
  @worker_required
  def post(self):
    labeling = Labeling()
    labeling.image_url = self.experiment.t1_image_url
    labeling.worker = self.worker
    labeling.labels = self.request.get_all('label')
    labeling.time = int(self.request.get('time'))
    labeling.put()

    negotiation = Negotiation()
    negotiation.worker = self.worker
    negotiation.first_offer = self.worker.group.opening_bid
    negotiation.put()

    self.json({'message': self.host_url('/offer/1')})


class Offer1(RequestHandler):
  @experiment_required
  @worker_required
  @negotiation_required
  def get(self):
    self.render('priv/offer_1.html', {
      'value': self.negotiation.first_offer
    , 'action': self.request.url
    })

  @experiment_required
  @worker_required
  @negotiation_required
  def post(self):
    reply = self.request.get('reply')

    time.sleep(random.uniform(0.5, 2))

    if reply == 'accept':
      self.negotiation.first_offer_accepted = True
      self.negotiation.put()

      self.json({'redirect': self.host_url('/task/2')})
    elif reply == 'reject':
      self.negotiation.first_offer_rejected = True
      self.negotiation.put()

      self.json({'redirect': self.mturk_submit_url()})
    elif reply == 'counter':
      try:
        counter_offer = int(self.request.get('offer'))
      except ValueError:
        self.bad_request('Bad offer')
        return

      if counter_offer >= 0 and counter_offer <= 99:
        self.negotiation.counter_offer = counter_offer

        employer_reply = hagglorithm.auto_haggle(counter_offer, self.worker.group)

        if type(employer_reply) == hagglorithm.Accept:
          self.negotiation.counter_offer_accepted = True
          self.negotiation.put()

          self.json({'redirect': self.host_url('/task/2')})
        elif type(employer_reply) == hagglorithm.Reject:
          self.negotiation.counter_offer_rejected = True
          self.negotiation.put()

          self.json({'redirect': self.mturk_submit_url()})
        else:
          self.negotiation.second_offer = employer_reply.value
          self.negotiation.put()

          self.json({'message': self.host_url('/offer/2')})
      else:
        self.bad_request('Bad offer')
    else:
      self.bad_request('Bad reply')


class Offer2(RequestHandler):
  @experiment_required
  @worker_required
  @negotiation_required
  def get(self):
    self.render('priv/offer_2.html', {
      'value': self.negotiation.second_offer
    , 'action': self.request.url
    })

  @experiment_required
  @worker_required
  @negotiation_required
  def post(self):
    reply = self.request.get('reply')

    time.sleep(random.uniform(0.5, 2))

    if reply == 'accept':
      self.negotiation.second_offer_accepted = True
      self.negotiation.put()

      self.json({'redirect': self.host_url('/task/2')})
    elif reply == 'reject':
      self.negotiation.second_offer_rejected = True
      self.negotiation.put()

      self.json({'redirect': self.mturk_submit_url()})
    else:
      self.bad_request('Bad reply')


class Task2(RequestHandler):
  @experiment_required
  @worker_required
  @negotiation_required
  def get(self):
    if negotiation_successful(self.negotiation):
      self.render('priv/task_2.html', {
        'image': self.experiment.t2_image_url
      , 'action': self.request.url
      })
    else:
      self.not_found()

  @experiment_required
  @worker_required
  @negotiation_required
  def post(self):
    labeling = Labeling()
    labeling.image_url = self.experiment.t2_image_url
    labeling.worker = self.worker
    labeling.labels = self.request.get_all('label')
    labeling.time = int(self.request.get('time'))
    labeling.put()

    # reward = negotiation_reward(self.negotiation)
    # 
    # response = mturk.grant_bonus(self.worker, self.experiment, reward)
    # 
    # if response.status is False:
    #   logging.error('could not grant bonus to workerId=' + self.worker.id)

    self.json({'redirect': self.mturk_submit_url()})


def handlers():
  return [
    ('/', Root)
  , ('/upload', Upload)
  , ('/confirm', Confirm)
  , ('/task/1', Task1)
  , ('/offer/1', Offer1)
  , ('/offer/2', Offer2)
  , ('/task/2', Task2)
  ]


def application():
  return webapp.WSGIApplication(handlers(), debug=True)


def main():
  run_wsgi(application())


if __name__ == '__main__':
  main()
