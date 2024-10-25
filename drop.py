#!/usr/bin/python3

from time import sleep, time

import logging
logging.basicConfig(format='[CONTROLLER] - %(levelname)s | %(message)s', level=logging.DEBUG)

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

#====================================================================================

def signalHandler(signum, frame, controller):
    print()
    logging.warning('Caught termination signal: %s' % signum)
    logging.info('Shutting down controller.')
    controller.stop()
    sys.exit()

#====================================================================================

async def send_command(function, *args):
  result = await IOLoop.current().run_in_executor(None, function, *args)
  return {'result': result}

#====================================================================================

class DefaultHandler(RequestHandler):
  def prepare(self):
    self.set_status(404)

class DelayPercentageHandler(RequestHandler):
  async def get(self):
    try:
      if result := await send_command(controller.get_delay_percentage):
        self.write(result)
      else:
        self.set_status(400)
        self.write({'detail':'unable to retrieve controller.get_delay_percentage.'})
    except Exception as e:
      self.set_status(500)
      self.write({'detail': f"DelayPercentageHandler: {repr(e)}"})

class MainHandler(RequestHandler):
  async def get(self):
    print(f"hostname: {hostname}")
    self.render(
      'index.html',
      hostname=hostname,
      port=config('PORT', default=8888, cast=int)
    )
  async def post(self):
    target = self.get_query_argument('target', None)
    function = None
    args = []
    try:
      body = json.loads(self.request.body.decode('utf-8'))
      parameters = body['parameters']
      match target:
        case 'register':
          function = controller.set_register_state
          args.append(parameters['state'])
        case 'tempo':
          function = controller.set_tempo
          args.append(parameters['value'])
        case 'mult_loop_delay':
          function = controller.mult_loop_delay
          args.append(parameters['value'])
        case 'div_loop_delay':
          function = controller.div_loop_delay
          args.append(parameters['value'])
        case 'loop_delay':
          function = controller.set_loop_delay
          args.append(parameters['value'])
        case 'nudge_delay':
          function = controller.nudge_loop_delay
          args.append(parameters['value'])
        case 'loop':
          if parameters['retrigger']:
            function = controller.start
          else:
            function = controller.stop
        case 'lfsr':
          function = controller.set_lfsr_parameters
          args.append(parameters)
        case 'strobe':
          function = controller.set_strobe_parameters
          args.append(parameters)

      if result := await send_command(function, *args):
        self.write(result)
      else:
        self.set_status(400)
        self.write({'detail':'unable to send_command to controller'})
    except Exception as e:
      logging.error('While parsing request: %s' % repr(e))
      self.set_status(500)

#====================================================================================

def make_app():
  path = os.path.dirname(os.path.abspath(__file__))

  settings = dict(
    template_path = os.path.join(path, 'templates'),
    static_path = os.path.join(path, 'static'),
    debug = True
  )

  urls = [
    (r'/delay', DelayPercentageHandler),
    (r'/', MainHandler)
  ]

  return Application(urls, **settings)

#====================================================================================

if __name__ == '__main__':

  try:
    hostname = os.uname()[1]
    if len(hostname.split('.')) != 2:
      hostname += '.local'

    controller = StrobeController()
    signalHandler = partial(signalHandler, controller=controller)
    signal.signal(signal.SIGTERM, signalHandler)
    signal.signal(signal.SIGHUP, signalHandler)
    signal.signal(signal.SIGINT, signalHandler)

    # make and run the controller web application
    application = make_app()
    http_server = HTTPServer(application)
    http_server.listen(
      config('PORT', default=8888, cast=int)
    )
    main_loop = IOLoop.current()
    main_loop.start()
  except Exception as e:
    logging.error('Doh! %s' % repr(e))
