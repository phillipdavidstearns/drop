'''
This is meant to control an array of 8 strobes.
The strobes are +edge triggered.
A CD4094 is used to provide the +edge trigger.
A 8-bit register is used to set the state of the CD4094.
An output on the CD4094 must transistion to 0 in order for it to re-trigger a strobe.
This controller coordinates between operations on the register and its output to the CD4094

Basic flow:

Strobe Controller > Register State  > CD4094 > CD4098 Mono stable > STROBE
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
    self.clock = Divider()
    self.delay_min = 0.025
    self.delay_max = 1
    self.lfsr_enabled = False
    self.lfsr_parameters = None
    self.output_enable = True
    self.strobe_enabled = False
    self.strobe_parameters = None
    self.strobe_invert_on_count=0
    self.strobe_invert_off_count=0
    self.strobe_invert_state=False
    self.strobe_mute_on_count=0
    self.strobe_mute_off_count=0
    self.strobe_mute_state=False

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

  def set_loop_delay(self, percentage):
    percentage = min(max(percentage, 0.0),1.0)
    delay = percentage * (self.delay_max - self.delay_min) + self.delay_min
    self.loop_delay = delay
    return self.loop_delay

  def nudge_loop_delay(self, percentage):
    new_loop_delay = self.loop_delay * ( percentage + 1.0 )
    if  new_loop_delay <= self.delay_max and new_loop_delay >= self.delay_min:
      self.loop_delay = new_loop_delay
      return self.loop_delay
    else:
      return False

  def set_tempo(self, tempo):
    if tempo <= self.delay_max and tempo >= self.delay_min:
      self.loop_delay = tempo
      return self.loop_delay
    else:
      return False

  def mult_loop_delay(self, value):
    new_loop_delay = self.loop_delay * value
    if  new_loop_delay <= self.delay_max and new_loop_delay >= self.delay_min:
      self.loop_delay = new_loop_delay
      return self.loop_delay
    else:
      return False

  def div_loop_delay(self, value):
    new_loop_delay = self.loop_delay / value
    if  new_loop_delay <= self.delay_max and new_loop_delay >= self.delay_min:
      self.loop_delay = new_loop_delay
      return self.loop_delay
    else:
      return False

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

  def set_lfsr_parameters(self, parameters):
    self.lfsr_parameters = parameters
    return self.lfsr_parameters

  def set_lfsr_enabled(self, value):
    self.lfsr_enabled=value
    return self.lfsr_enabled

  def lfsr(self):
    input_bit = 0
    for tap in self.lfsr_parameters['taps']:
      input_bit ^= self.get_register_bit(tap)
    if self.lfsr_parameters['modEnabled']:
      input_bit ^= self.clock.get_bit(
        self.lfsr_parameters['modSource'],
        self.lfsr_parameters['modQ']
      )
    if self.lfsr_parameters['direction'] == 'left':
      self.shift_register_left(input_bit)
    elif self.lfsr_parameters['direction'] == 'right':
      self.shift_register_right(input_bit)
    return self.register.get_state()

  def set_strobe_parameters(self, parameters):
    self.strobe_parameters = parameters
    if self.strobe_parameters['mute_enabled'] == False:
      self.output_enable = True
    return self.strobe_parameters

  def set_strobe_enabled(self, value):
    self.strobe_enabled = value
    if self.strobe_enabled == False:
      self.output_enable = True
    return self.strobe_enabled
  
  def strobe(self):
    if self.strobe_parameters['invert_enabled']:
      if self.strobe_invert_state == False:
        if self.strobe_invert_off_count < self.strobe_parameters['invert_off']:
          self.strobe_invert_off_count+=1
        elif self.strobe_invert_off_count >= self.strobe_parameters['invert_off']:
          self.invert_register()
          self.strobe_invert_state = True
          self.strobe_invert_on_count=0
      elif self.strobe_invert_state == True:
        if self.strobe_invert_on_count < self.strobe_parameters['invert_on']:
          self.strobe_invert_on_count+=1
        elif self.strobe_invert_on_count >= self.strobe_parameters['invert_on']:
          self.invert_register()
          self.strobe_invert_state = False
          self.strobe_invert_off_count = 0

    if self.strobe_parameters['mute_enabled']:
      if self.strobe_mute_state == False:
        if self.strobe_mute_off_count < self.strobe_parameters['mute_off']:
            self.strobe_mute_off_count+=1
        elif self.strobe_mute_off_count >= self.strobe_parameters['mute_off']:
          self.output_enable = True
          self.strobe_mute_state = True
          self.strobe_mute_on_count=0
      elif self.strobe_mute_state == True:
        if self.strobe_mute_on_count < self.strobe_parameters['mute_on']:
          self.strobe_mute_on_count+=1
        elif self.strobe_mute_on_count >= self.strobe_parameters['mute_on']:
          self.output_enable = False
          self.strobe_mute_state = False
          self.strobe_mute_off_count = 0

  def loop(self):
    try:
      if self.retrigger and not self.shutdown:
        self.timer = Timer(self.loop_delay, self.loop)
        self.timer.daemon = True
        self.timer.start()

        if self.output_enable:
          self.update()
          self.output.enable()
        else:
          self.output.disable()
          self.update()

        if self.lfsr_enabled: self.lfsr()
        if self.strobe_enabled: self.strobe()

    except Exception as e:
      logging.error('in StrobeController.loop(): %s' % repr(e))