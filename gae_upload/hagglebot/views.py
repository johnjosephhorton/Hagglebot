from hagglebot.util import cents_to_dollars

from urlparse import urlparse

from os.path import basename


class Image(object):
  def __init__(self, url):
    self.basename = basename(urlparse(url).path)
    self.url = url


class ConfirmView(object):
  def __init__(self, experiment, groups):
    self.aws_access_key_id = experiment.aws_access_key_id
    self.aws_secret_access_key = experiment.aws_secret_access_key
    self.aws_hostname = experiment.aws_hostname
    self.hit_title = experiment.hit_title
    self.hit_description = experiment.hit_description
    self.hit_lifetime = experiment.hit_lifetime
    self.hit_max_assignments = experiment.hit_max_assignments
    self.hit_keywords = ', '.join(experiment.hit_keywords)
    self.hit_duration = experiment.hit_duration
    self.hit_approval_delay = experiment.hit_approval_delay
    self.hit_frame_height = experiment.hit_frame_height
    self.t1_image = Image(experiment.t1_image_url)
    self.t1_reward = cents_to_dollars(experiment.t1_reward)
    self.t2_image = Image(experiment.t2_image_url)
    self.groups = groups
