from boto.mturk.connection import MTurkConnection
from boto.mturk.question import ExternalQuestion
from boto.mturk.price import Price

from haggleliza.util import cents_to_dollars


def connect(experiment):
  return MTurkConnection(
    aws_access_key_id=experiment.aws_access_key_id
  , aws_secret_access_key=experiment.aws_secret_access_key
  , host=experiment.aws_hostname
  )


def approve(assignment_id, experiment):
  mturk = connect(experiment)

  return mturk.approve_assignment(assignment_id)


def create_hit(url, experiment):
  mturk = connect(experiment)

  return mturk.create_hit(
    question=ExternalQuestion(url, experiment.hit_frame_height)
  , title=experiment.hit_title
  , description=experiment.hit_description
  , lifetime=experiment.hit_lifetime
  , max_assignments=experiment.hit_max_assignments
  , keywords=experiment.hit_keywords
  , duration=experiment.hit_duration
  , approval_delay=experiment.hit_approval_delay
  , reward=cents_to_dollars(experiment.t1_reward)
  , response_groups=['Minimal', 'HITDetail', 'HITQuestion', 'HITAssignmentSummary']
  )


def grant_bonus(worker, experiment, reward):
  mturk = connect(experiment)

  reason = 'Additional reward for second image labeling task'

  return mturk.grant_bonus(
    worker.id
  , worker.assignment_id
  , Price(cents_to_dollars(reward))
  , reason
  )
