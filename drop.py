#!/usr/bin/python3

from time import sleep, time
import logging
import random
import signal
import os
import sys
from functools import partial
from decouple import config
from tornado.web import Application, RequestHandler, StaticFileHandler
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
import json

from StrobeController import StrobeController
from Operations import *

path = os.path.dirname(os.path.abspath(__file__))

#====================================================================================

def randomData(qty_bits=8):
  bits=[]
  for i in range(qty_bits):
    bits.append(round(random.random()))
  logging.debug('randomBits: %s' % repr(bits))
  return bits

#====================================================================================

def signalHandler(signum, frame, controller):
    print()
    logging.warning('Caught termination signal: %s' % signum)
    logging.info('Shutting down controller.')
    controller.stop()
    sys.exit()

#====================================================================================
# Helper functions for direct control

def set_loop_retrigger(parameters):
  if parameters['retrigger'] == True:
    return controller.start_loop()
  elif parameters['retrigger'] == False:
    return controller.stop_loop()
  else:
    return False

#====================================================================================

class DefaultHandler(RequestHandler):
  def prepare(self):
    self.set_status(404)

class MainHandler(RequestHandler):
  async def get(self):
    self.render('index.html', hostname=os.uname()[1])
  async def post(self):
    result = None
    try:
      body = json.loads(self.request.body.decode('utf-8'))
      if body['type'] == 'get':
        if body['target'] == 'delay_percentage':
          result = await IOLoop.current().run_in_executor(
            None,
            controller.get_delay_percentage
          )
      elif body['type'] == 'set':
        if body['target'] == 'register':
          result = await IOLoop.current().run_in_executor(
            None,
            controller.set_register_state,
            body['parameters']['state']
          )
        elif body['target'] == 'tempo':
          result = await IOLoop.current().run_in_executor(
            None,
            controller.set_tempo,
            body['parameters']['value']
          )
        elif body['target'] == 'mult_loop_delay':
          result = await IOLoop.current().run_in_executor(
            None,
            controller.mult_loop_delay,
            body['parameters']['value']
          )
        elif body['target'] == 'div_loop_delay':
          result = await IOLoop.current().run_in_executor(
            None,
            controller.div_loop_delay,
            body['parameters']['value']
          )
        elif body['target'] == 'loop_delay':
          result = await IOLoop.current().run_in_executor(
            None,
            controller.set_loop_delay,
            body['parameters']['value']
          )
        elif body['target'] == 'nudge_delay':
          result = await IOLoop.current().run_in_executor(
            None,
            controller.nudge_loop_delay,
            body['parameters']['value']
          )
        elif body['target'] == 'loop':
          result = await IOLoop.current().run_in_executor(
            None,
            set_loop_retrigger,
            body['parameters']
          )
        elif body['target'] == 'lfsr':
          result = await IOLoop.current().run_in_executor(
            None,
            controller.set_lfsr_parameters,
            body['parameters']
          )
        elif body['target'] == 'lfsr_enabled':
          result = await IOLoop.current().run_in_executor(
            None,
            controller.set_lfsr_enabled,
            True
          )
        elif body['target'] == 'lfsr_disabled':
          result = await IOLoop.current().run_in_executor(
            None,
            controller.set_lfsr_enabled,
            False
          )
        elif body['target'] == 'strobe':
          result = await IOLoop.current().run_in_executor(
            None,
            controller.set_strobe_parameters,
            body['parameters']
          )
        elif body['target'] == 'strobe_enabled':
          result = await IOLoop.current().run_in_executor(
            None,
            controller.set_strobe_enabled,
            True
          )
        elif body['target'] == 'strobe_disabled':
          result = await IOLoop.current().run_in_executor(
            None,
            controller.set_strobe_enabled,
            False
          )
      if result:
        self.set_status(200)
      else:
        self.set_status(400)
    except Exception as e:
      logging.error('While parsing request: %s' % repr(e))
      self.set_status(500)
    finally:
      self.write({'result':result})

#====================================================================================

def make_app():
  settings = dict(
    template_path = os.path.join(path, 'templates'),
    static_path = os.path.join(path, 'static'),
    debug = True
  )

  urls = [
    (r'/', MainHandler)
  ]

  return Application(urls, **settings)

#====================================================================================

if __name__ == '__main__':

  try:
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    
    controller = StrobeController()

    signalHandler = partial(signalHandler, controller=controller)
    signal.signal(signal.SIGTERM, signalHandler)
    signal.signal(signal.SIGHUP, signalHandler)
    signal.signal(signal.SIGINT, signalHandler)

    # make and run the controller web application
    application = make_app()
    http_server = HTTPServer(application)
    http_server.listen(80)
    main_loop = IOLoop.current()
    main_loop.start()
  except Exception as e:
    print('Doh! %s' % repr(e))
