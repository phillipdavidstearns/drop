import logging

################################################################
# CLASS DEFINITION: Register

class Counter():
  #limiting the counter to 
  def __init__(self, count=None):
    logging.info('[Counter] Creating a new Counter.')
    self.count = 0
    if count:
      self.set_state(count)

  def set(self, count):
    self.count =  min(max(0,int(count)),0xffffffffffffffff)
    return self.count

  def reset(self,state):
    self.count = 0
    return self.count

  def get_bit(self, q):
    return self.count >> min(max(0,int(q)),0xffffffffffffffff) & 0b1

  def inc(self):
    self.count += 1
    return self.count

  def dec(self):
    if self.count > 0:
      self.count -= 1
    return self.count

  def get(self):
    return self.count

class Divider():
  def __init__(self, divisions=[1,3,5,7,9,11,13]):
    self.divisions=divisions
    self.count=Counter()
    self.clocks=[]
    for i in range(len(self.divisions)):
      self.clocks.append(Counter())

  def inc(self):
    for i in range(len(self.clocks)):
      if self.count.get() % self.divisions[i] == 0:
        self.clocks[i].inc()
    self.count.inc()

  def get_clock(self, div):
    return self.clocks[div].get()

  def get_bit(self, div, q):
    return self.clocks[div].get_bit(q)
