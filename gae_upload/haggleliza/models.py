from google.appengine.ext import db as datastore


class Experiment(datastore.Model):
  created = datastore.DateTimeProperty(auto_now_add=True)
  aws_access_key_id = datastore.StringProperty()
  aws_secret_access_key = datastore.StringProperty()
  aws_hostname = datastore.StringProperty()
  hit_id = datastore.StringProperty()
  hit_title = datastore.StringProperty()
  hit_description = datastore.StringProperty()
  hit_lifetime = datastore.IntegerProperty()
  hit_max_assignments = datastore.IntegerProperty()
  hit_keywords = datastore.StringListProperty()
  hit_duration = datastore.IntegerProperty()
  hit_approval_delay = datastore.IntegerProperty()
  hit_frame_height = datastore.IntegerProperty()
  t1_image_url = datastore.StringProperty()
  t1_reward = datastore.IntegerProperty()
  t2_image_url = datastore.StringProperty()
  group_count = datastore.IntegerProperty()
  group_index = datastore.IntegerProperty()


class Group(datastore.Model):
  created = datastore.DateTimeProperty(auto_now_add=True)
  experiment = datastore.ReferenceProperty(Experiment)
  nickname = datastore.StringProperty()
  opening_bid = datastore.IntegerProperty()
  accept_thresh = datastore.IntegerProperty()
  reject_thresh = datastore.IntegerProperty()
  alpha = datastore.FloatProperty()


class Worker(datastore.Model):
  created = datastore.DateTimeProperty(auto_now_add=True)
  id = datastore.StringProperty()
  assignment_id = datastore.StringProperty()
  group = datastore.ReferenceProperty(Group)


class Labeling(datastore.Model):
  created = datastore.DateTimeProperty(auto_now_add=True)
  image_url = datastore.StringProperty()
  worker = datastore.ReferenceProperty(Worker)
  labels = datastore.StringListProperty()
  time = datastore.IntegerProperty()


class Negotiation(datastore.Model):
  created = datastore.DateTimeProperty(auto_now_add=True)
  worker = datastore.ReferenceProperty(Worker)
  first_offer = datastore.IntegerProperty()
  first_offer_accepted = datastore.BooleanProperty(default=False)
  first_offer_rejected = datastore.BooleanProperty(default=False)
  counter_offer = datastore.IntegerProperty()
  counter_offer_accepted = datastore.BooleanProperty(default=False)
  counter_offer_rejected = datastore.BooleanProperty(default=False)
  second_offer = datastore.IntegerProperty()
  second_offer_accepted = datastore.BooleanProperty(default=False)
  second_offer_rejected = datastore.BooleanProperty(default=False)
