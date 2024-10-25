from threading import Timer
import logging
from decouple import config

class Interval(Timer):
  MIN = config('MIN_DELAY', default=0.025, cast=float);
  MAX = config('MAX_DELAY', default=2.0, cast=float);

  def __init__(self, interval, function):
    super().__init__(interval, function)
    self.daemon = True
    self._interval = interval
    self._function = function

  def run(self):
    while not self.finished.wait(self._interval):
      self._function(*self.args, **self.kwargs)

  @property
  def is_running(self):
    return self.is_alive()

  @property
  def interval(self):
    return self._interval

  @interval.setter
  def interval(self, interval):
    self._interval = max(self.MIN, min(float(interval), self.MAX))

  @property
  def function(self):
    return self._function

  @function.setter
  def function(self, function):
    self._function = function

  def stop(self):
    self.cancel()

if __name__ == '__main__':

  import signal
  import os
  from time import sleep

  def signalHandler(signum, frame):
    print()
    logging.warning('Caught termination signal: %s' % signum)
    shutdown(status=1)

  def shutdown(status=1):
    interval.stop()
    os._exit(status)

  signal.signal(signal.SIGTERM, signalHandler)
  signal.signal(signal.SIGHUP, signalHandler)
  signal.signal(signal.SIGINT, signalHandler)

  logging.basicConfig(
    format='[INTERVAL] - %(levelname)s | %(message)s',
    level=logging.DEBUG
  )

  try:
    interval = Interval(1.0, lambda: print('Hello World!'))
    interval.start()
    while interval.is_running:
      sleep(1)

  except Exception as e:
    logging.error('Uncaught while running main(): %s' % repr(e))
  finally:
    shutdown(status=0)
