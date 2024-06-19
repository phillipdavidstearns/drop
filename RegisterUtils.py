import logging

################################################################
# CLASS DEFINITION: Register

class Register():
  def __init__(self, length=8, state=0):
    self._length = length
    self._state = state

  @property
  def state(self):
    return self._state

  @state.setter
  def state(self, state):
    mask = pow(2,self._length)-1
    self._state = state & mask
    return self._state

  @property
  def length(self):
    return self._length

  @length.setter
  def length(self, length):
    if length <= 0:
      raise Exception('length must be greater than 0')
    self._length = length
    mask = pow(2,self._length)-1
    self._state = state & mask
    return self._state

  def reset(self):
    self._state = 0
    return self._state

  def invert(self):
    mask = pow(2,self._length)-1
    self._state = self._state ^ mask
    return self._state

  def get_bit(self, index):
    if index > self._length or index < 0:
      raise Exception(f"index {index} out of bounds ({self._length - 1})")
    return (self._state >> index ) & 0b1

  def set_bit(self, index, bit):
    if index > self._length or index < 0:
      raise Exception(f"index {index} out of bounds ({self._length - 1})")
    mask = pow(2, self._length) - 1
    mask ^= 0b1 << index
    self._state &= mask
    self._state |= (bit & 0b1) << index
    return self._state

  def shift_right(self, bit=0):
    self._state >>= 1
    self.set_bit(self._length - 1, bit)
    return self._state

  def shift_left(self, bit=0):
    self._state <<= 1
    mask = pow(2, self._length) - 1
    self._state &= mask
    self.set_bit(0, bit)
    return self._state

  def lfsr_left(self, bit, tap1, tap2):
    input_bit = bit ^ self.get_bit(tap1) ^ self.get_bit(tap2)
    self.shift_left(input_bit)
    return self._state

  def lfsr_right(self, bit, tap1, tap2):
    input_bit = bit ^ self.get_bit(tap1) ^ self.get_bit(tap2)
    self.shift_right(input_bit)
    return self._state

  def reverse(self):
    new_state = 0
    for i in range(self._length):
      new_state |= (self._state >> i & 0b1) << ((self._length - 1) - i)
    self._state = new_state
    return self._state

  def increment(self):
    self._state += 1
    self._state %= pow(2,self._length)
    return self._state

  def decrement(self):
    self._state -= 1
    self._state %= (pow(2,self._length))
    return self._state

class Divider():
  def __init__(self, divisions=[1,3,5,7,9,11,13]):
    self.divisions = divisions
    self.count = Register(length=32)
    self.clocks = []
    for i in range(len(self.divisions)):
      self.clocks.append(Register(length=32))

  def inc(self):
    for i in range(len(self.clocks)):
      if self.count.state % self.divisions[i] == 0:
        self.clocks[i].increment()
    self.count.increment()

  def get_clock(self, div):
    return self.clocks[div].state

  def get_bit(self, div, q):
    return self.clocks[div].get_bit(q)