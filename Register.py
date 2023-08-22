import logging

LEFT = 0
RIGHT = 1

################################################################
# CLASS DEFINITION: Register

class Register():
  def __init__(self, size=8, state=None):
    logging.info('[Register] Creating a new Register.')
    self.register = [0]*size
    if state:
      self.set_state(state)

  def set_state(self, state):
    self.register = [ int(bit) & 0b1 for bit in state ]
    return self.register.copy()

  def reset(self):
    self.register = [0]*len(self.register)
    return self.register.copy()

  def invert(self):
    self.register = [ 1 ^ bit & 0b1 for bit in self.register ]
    return self.register.copy()

  def get_bit(self, index):
    return self.register[index]

  def set_bit(self, index, bit):
    self.register[index]=int(bit) & 0b1
    return self.register.copy()

  def shift_right(self, bit=0):
    self.register = self.register[1:]
    self.register.append(int(bit) & 0b1)
    return self.register.copy()

  def reverse(self):
    self.register.reverse()
    return self.register.copy()

  def shift_left(self, bit=0):
    shifted = []
    shifted.append(int(bit) & 0b1)
    shifted += self.register[:-1]
    self.register = shifted.copy()
    return self.register.copy()

  def lfsr_left(self, bit, tap1, tap2):
    input_bit = bit ^ self.register.get_bit[tap1] ^ self.register.get_bit[tap2] 
    self.shift_left(input_bit)
    return self.register.copy()

  def lfsr_right(self, bit, tap1, tap2):
    input_bit = bit ^ self.register.get_bit[tap1] ^ self.register.get_bit[tap2] 
    self.shift_right(input_bit)
    return self.register.copy()

  def get_state(self):
    return self.register.copy()

  def size(self):
    return len(self.register)