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

from threading import Timer
import logging
from RegisterUtils import Register, Divider
from time import sleep
from decouple import config
from interval import Interval

try:
  from CD4094 import CD4094
except Exception as e:
  logging.warning(f"Unable to load CD4094: {repr(e)}")

################################################################
# CLASS DEFINITION: StrobeController

class StrobeController():
  def __init__(self, delay=1, channels=8):
    self.loop_delay = delay
    self.channels = channels
    self.register = Register(length=channels)
    try:
      self.output = CD4094(channels=channels)
    except Exception as e:
      logging.warning(f"Unable to initalize CD4094: {repr(e)}")
      self.output = None
    self.clock = Divider()
    self.delay_min = config('MIN_DELAY', default=0.025,cast=float);
    logging.debug(f"self.delay_min: {self.delay_min}")
    self.delay_max = config('MAX_DELAY', default=2.0,cast=float);
    logging.debug(f"self.delay_max: {self.delay_max}")
    self.lfsr_enabled = False
    self.lfsr_parameters = None
    self.output_enabled = True
    self.strobe_enabled = False
    self.strobe_parameters = None
    self.strobe_invert_on_count = 0
    self.strobe_invert_off_count = 0
    self.strobe_invert_state = False
    self.strobe_mute_on_count = 0
    self.strobe_mute_off_count = 0
    self.strobe_mute_state = False
    self._interval = None

  def update_interval(self):
    if self._interval:
      self._interval.interval = self.loop_delay

  #-------Start and Stop Looping/Retriggering-------

  def start(self):
    if not self._interval:
      self._interval = Interval(self.loop_delay, self.update)

    if not self._interval.is_running:
      self._interval.start()

  def stop(self):
    if self._interval:
      self._interval.stop()
      self._interval = None

  #-------Loop Delay Setter-------

  def get_delay_percentage(self):
    return (self.loop_delay -  self.delay_min) / (self.delay_max - self.delay_min)

  def set_loop_delay(self, percentage):
    percentage = min(max(percentage, 0.0),1.0)
    delay = percentage * (self.delay_max - self.delay_min) + self.delay_min
    self.loop_delay = delay
    self.update_interval()
    return self.get_delay_percentage()

  def nudge_loop_delay(self, percentage):
    new_loop_delay = self.loop_delay * ( percentage + 1.0 )
    if  new_loop_delay <= self.delay_max and new_loop_delay >= self.delay_min:
      self.loop_delay = new_loop_delay
      self.update_interval()
    return self.get_delay_percentage()

  def set_tempo(self, tempo):
    if tempo <= self.delay_max and tempo >= self.delay_min:
      self.loop_delay = tempo
      self.update_interval()
    return self.get_delay_percentage()

  def mult_loop_delay(self, value):
    new_loop_delay = self.loop_delay * value
    if  new_loop_delay <= self.delay_max and new_loop_delay >= self.delay_min:
      self.loop_delay = new_loop_delay
      self.update_interval()
    return self.get_delay_percentage()

  def div_loop_delay(self, value):
    new_loop_delay = self.loop_delay / value
    if  new_loop_delay <= self.delay_max and new_loop_delay >= self.delay_min:
      self.loop_delay = new_loop_delay
      self.update_interval()
    return self.get_delay_percentage()


  #-------Register Bit Getter and Setter-------

  def get_register_bit(self, index):
    return self.register.get_bit(index)

  def set_register_bit(self, index, value):
    return self.register.set_bit(index, value)

  #-------Register State Getter and Setter-------

  def get_register_state(self):
    return self.register.state

  def set_register_state(self, state):
    value = 0
    for i in range(len(state)):
      value |= state[i] << i
    self.register.state = value
    return self.register.state

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
    if self.output:
      if self.output_enabled:
         self.output.enable()
      else:
        self.output.disable()
      self.output.update(self.register.state)
    self.clock.inc()
    if self.lfsr_enabled: self.lfsr()
    if self.strobe_enabled: self.strobe()

  def set_lfsr_parameters(self, parameters):
    self.lfsr_parameters = parameters
    if 'is_enabled' in self.lfsr_parameters:
      self.set_lfsr_enabled(self.lfsr_parameters['is_enabled'])
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
    match self.lfsr_parameters['direction']:
      case 'left':
        self.shift_register_left(input_bit)
      case 'right':
        self.shift_register_right(input_bit)
    return self.register.state

  def set_strobe_parameters(self, parameters):
    self.strobe_parameters = parameters
    if self.strobe_parameters['mute_enabled'] == False:
      self.output_enabled = True
    if 'is_enabled' in self.strobe_parameters:
      self.set_strobe_enabled(self.strobe_parameters['is_enabled'])
    return self.strobe_parameters

  def set_strobe_enabled(self, value):
    self.strobe_enabled = value
    if self.strobe_enabled == False:
      self.output_enabled = True
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
          self.output_enabled = True
          self.strobe_mute_state = True
          self.strobe_mute_on_count=0
      elif self.strobe_mute_state == True:
        if self.strobe_mute_on_count < self.strobe_parameters['mute_on']:
          self.strobe_mute_on_count+=1
        elif self.strobe_mute_on_count >= self.strobe_parameters['mute_on']:
          self.output_enabled = False
          self.strobe_mute_state = False
          self.strobe_mute_off_count = 0
