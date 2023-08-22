'''
This is meant to control an array of 8 strobes.
The strobes are +edge triggered.
A CD4094 is used to provide the +edge trigger.
A 8-bit register is used to set the state of the CD4094.
An output on the CD4094 must transistion to 0 in order for it to re-trigger a strobe.
This controller coordinates between operations on the register and its output to the CD4094

Basic flow:

Strobe Controller > Register State  > CD4094 > CD4098 Mono stable > STROBE

Some of the things I might want to do:

Shift Left (LFSR)
Shift Right (LFSR)
Change the feedback taps


'''

from threading import Thread, Timer, Lock
import logging

from CD4094 import CD4094
from Register import *
from Operations import *
from Counter import *

################################################################
# CLASS DEFINITION: StrobeController

class StrobeController():
  def __init__(self, delay=1, channels=8):
    self.loop_delay = delay
    self.channels = channels
    self.timer = None
    self.register = Register(size=channels)
    self.last_register_state = Register(size=channels)
    self.output = CD4094(channels=channels)
    self.retrigger = False
    self.shutdown = False
    self.stack = OperationStack()
    self.clock = Divider()
    self.delay_min = 0.03333333
    self.delay_max = 1
    self.mode = 'shift'
    self.delay_percentage = 0

  #-------Main Thread/Process Start and Stop-------


  def stop(self):
    self.retrigger = False
    self.shutdown = True
    try:
      self.timer.cancel()
    except:
      pass
    self.output.stop()

  #-------Start and Stop Looping/Retriggering-------

  def start_loop(self):
    if self.retrigger == False: 
      self.retrigger = True
      self.loop()
      return True
    else:
      return False

  def stop_loop(self):
    self.retrigger = False
    try:
      self.timer.cancel()
    except:
      pass
    return True

  #-------Loop Delay Setter-------

  def set_mode(self, mode):
    if mode != self.mode:
      self.mode = mode
      if self.mode == 'strobe':
        self.loop_delay = min(max(self.loop_delay, self.delay_min), self.delay_max)
      elif self.mode == 'shift':
       self.loop_delay = min(max(self.loop_delay, 0.75 * self.delay_min), self.delay_max)
      return self.loop_delay
    else:
      return False

  def set_delay(self, percentage):
    self.delay_percentage = percentage
    if self.mode == 'strobe':
      delay = percentage * (self.delay_max - self.delay_min) + self.delay_min
      self.loop_delay = delay
    elif self.mode == 'shift':
      delay = percentage * (self.delay_max - ( 0.75 * self.delay_min )) + (0.75 * self.delay_min)
      self.loop_delay = delay
    else:
      return False
    return self.loop_delay

  def nudge_loop_delay(self, percentage):
    nudge_amount = self.loop_delay * ( 1.0 + percentage)
    if self.mode == 'strobe':
      if  new_loop_delay <= self.delay_max and new_loop_delay >= self.delay_min:
        self.loop_delay += new_loop_delay
    elif self.mode == 'shift':
      if new_loop_delay <= self.delay_max and new_loop_delay >= ( 0.75 * self.delay_min ):
        self.loop_delay = new_loop_delay
    else:
      return False
    self.delay_percentage = ( self.loop_delay - self.delay_min ) / ( self.delay_max - self.delay_min )
    return self.loop_delay

  def mult_loop_delay(self, value):
    new_loop_delay = self.loop_delay * value
    if self.mode == 'strobe':
      if  new_loop_delay <= self.delay_max and new_loop_delay >= self.delay_min:
        self.loop_delay = new_loop_delay
    elif self.mode == 'shift':
      if new_loop_delay <= self.delay_max and new_loop_delay >= ( 0.75 * self.delay_min ):
        self.loop_delay = new_loop_delay
    else:
      return False
    return self.loop_delay

  def div_loop_delay(self, value):
    new_loop_delay = self.loop_delay / value
    if self.mode == 'strobe':
      if  new_loop_delay <= self.delay_max and new_loop_delay >= self.delay_min:
        self.loop_delay = new_loop_delay
    elif self.mode == 'shift':
      if new_loop_delay <= self.delay_max and new_loop_delay >= ( 0.75 * self.delay_min ):
        self.loop_delay = new_loop_delay
    else:
      return False
    return self.loop_delay

  #-------Register Bit Getter and Setter-------

  def get_register_bit(self, index):
    return self.register.get_bit(index)

  def set_register_bit(self, index, value):
    return self.register.set_bit(index, value)

  #-------Register State Getter and Setter-------

  def get_register_state(self):
    return self.register.get_state()

  def set_register_state(self, state):  
    return self.register.set_state(state)

  #-------Register Shift Left/Right-------

  def shift_register_left(self, bit=0):
    return self.register.shift_left(bit)

  def shift_register_right(self, bit=0):
    return self.register.shift_right(bit)

  def invert_register(self):
    return self.register.invert()

  def reset_register(self):
    return self.register.reset()

  def update(self):
    register_state = self.register.get_state()
    if not ( register_state == self.last_register_state):
      self.output.update(register_state)
    self.last_register_state = register_state
    self.clock.inc()
    return register_state

  def loop(self):
    try:
      if self.retrigger and not self.shutdown:
        self.timer = Timer(self.loop_delay, self.loop)
        self.timer.daemon = True
        self.timer.start()
        self.update()
        self.stack.execute()
    except Exception as e:
      logging.error('in StrobeController.loop(): %s' % repr(e))

  def push(self, operation):
    self.stack.push(operation)

  def pop(self):
    self.stack.pop()

  def clear_operations(self):
    self.stack.clear()

if __name__ == '__main__':
  import sys
  from time import sleep

  def shift_left_loop(controller):
    controller.shift_register_left(controller.get_register_bit(7))

  def speed_up(controller):
    delay_min = 0.00625
    if controller.loop_delay > delay_min:
      controller.set_delay(controller.loop_delay * 0.95)
    elif controller.loop_delay < delay_min:
      controller.loop_delay = delay_min
    elif controller.loop_delay == delay_min:
      controller.stop_loop()
      controller.clear_operations()
      controller.reset_register()
      controller.set_delay(0.0125)
      controller.push(Operation(controller.invert_register))
      controller.push(Operation(slow_down,{'controller':controller}))
      controller.start_loop()

  def slow_down(controller):
    delay_max = 1.0
    if controller.loop_delay < delay_max:
      controller.set_delay(controller.loop_delay * 1.05)
    elif controller.loop_delay > delay_max:
      controller.loop_delay = delay_max
    elif controller.loop_delay == delay_max:
      controller.stop_loop()
      controller.clear_operations()
      controller.reset_register()
      controller.set_register_bit(0,1)
      controller.push(Operation(lfsr,{'controller':controller,'taps':[3,4,5]}))
      controller.push(Operation(speed_up,{'controller':controller}))
      controller.start_loop()

  def lfsr(controller, taps=[], mod=0):
    input_bit = 0
    for tap in taps:
      input_bit ^= controller.get_register_bit(tap)
    input_bit ^= mod
    controller.shift_register_left(input_bit)

  try:
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    
    logging.debug('controller = StrobeController()')
    controller = StrobeController()
    controller.set_register_bit(0,1)
    controller.push(Operation(shift_left_loop,{'controller':controller}))
    controller.push(Operation(speed_up,{'controller':controller}))
    controller.start_loop()

    while True:
      sleep(1)
    
  except Exception as e:
    print('Doh! %s' % repr(e))
  finally:
    controller.stop()
    sys.exit()