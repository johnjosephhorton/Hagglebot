class Accept(object):
  def __init__(self, counter_offer):
    self.counter_offer = counter_offer


class Reject(object):
  def __init__(self, counter_offer):
    self.counter_offer = counter_offer


class Offer(object):
  def __init__(self, value):
    self.value = value


def auto_haggle(counter_offer, group):
  if counter_offer <= group.accept_thresh:
    return Accept(counter_offer)
  elif counter_offer >= group.reject_thresh:
    return Reject(counter_offer)
  else:
    value = int(group.alpha * counter_offer + (1 - group.alpha) * group.accept_thresh)

    return Offer(value)


if __name__ == '__main__':
  class Group(object):
    def __init__(self, accept, reject, alpha):
      self.accept_thresh = accept
      self.reject_thresh = reject
      self.alpha = alpha

  group = Group(10, 20, 0.5)

  for counter_offer in (10, 12, 15, 17, 20):
    reply = auto_haggle(counter_offer, group)

    if type(reply) == Accept:
      print 'Counter offer of', counter_offer, 'cents ACCEPTED'
    elif type(reply) == Reject:
      print 'Counter offer of', counter_offer, 'cents REJECTED'
    elif type(reply) == Offer:
      print 'Counter offer of', counter_offer, 'cents REJECTED. New offer of', reply.value, 'cents'
