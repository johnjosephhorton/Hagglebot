from google.appengine.ext import db as datastore

from hagglebot.models import Group, Worker, Negotiation, Experiment

from decimal import Decimal


def cents_to_dollars(cents):
  return str((Decimal(cents) / Decimal(100)).quantize(Decimal('0.01')))


def next_group(experiment):
  def _fn(experiment_key):
    experiment = datastore.get(experiment_key)
    index = experiment.group_index
    experiment.group_index = (experiment.group_index + 1) % experiment.group_count
    experiment.put()
    return index

  index = datastore.run_in_transaction(_fn, experiment.key())

  groups = Group.all().filter('experiment = ', experiment)

  return list(groups)[index]


def worker_lookup(worker_id, assignment_id):
  return Worker.all().filter('id = ', worker_id).filter('assignment_id = ', assignment_id).get()


def worker_required(fn):
  def _fn(self, *args, **kwargs):
    workerId = self.request.get('workerId', None)

    assignmentId = self.request.get('assignmentId', None)

    if workerId is None:
      self.bad_request('No workerId')
    elif assignmentId is None:
      self.bad_request('No assignmentId')
    else:
      try:
        self.worker = worker_lookup(workerId, assignmentId)

        if self.worker is None:
          self.not_found()
        else:
          return fn(self, *args, **kwargs)
      except datastore.BadKeyError:
        self.not_found()

  return _fn


def negotiation_lookup(worker):
  return Negotiation.all().filter('worker = ', worker).get()


def negotiation_reward(negotiation):
  if negotiation.first_offer_accepted:
    return negotiation.first_offer
  elif negotiation.counter_offer_accepted:
    return negotiation.counter_offer
  elif negotiation.second_offer_accepted:
    return negotiation.second_offer
  else:
    return None


def negotiation_successful(negotiation):
  return not (negotiation_reward(negotiation) is None)


def negotiation_required(fn):
  def _fn(self, *args, **kwargs):
    negotiation = negotiation_lookup(self.worker)

    if negotiation is None:
      self.internal_server_error('No negotiation')
    else:
      self.negotiation = negotiation

      return fn(self, *args, **kwargs)

  return _fn


def experiment_required(fn):
  def _fn(self, *args, **kwargs):
    key = self.request.get('key', None)

    if key is None:
      self.bad_request('No key')
    else:
      try:
        self.experiment = Experiment.get(key)

        if self.experiment is None:
          self.not_found()
        else:
          return fn(self, *args, **kwargs)
      except datastore.BadKeyError:
        self.not_found()

  return _fn
