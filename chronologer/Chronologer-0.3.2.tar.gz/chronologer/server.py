import logging.config

import cherrypy

try:
  import chronologerui
except ImportError:
  chronologerui = None

from . import storage, controller


__all__ = 'bootstrap',


def bootstrap(config):
  '''Bootstrap application server'''

  logging.config.dictConfig(config['logging'])

  # Make cherrypy.process.wspbus.Bus.block interval shorter to reduce idle CPU usage
  cherrypy.engine.block.__func__.__defaults__ = 1,

  # If "global" is present it'll be used alone
  cherrypy.config.update(config.pop('global'))
  cherrypy.config.update(config)

  storageObj = storage.createStorage(config['storage']['dsn'])

  apps = []
  apps.append(cherrypy.tree.mount(controller.RecordApi(), '/api/v1/record', config['app']['api']))
  if chronologerui:
    apps.append(cherrypy.tree.mount(chronologerui.Ui(), '/', config['app']['ui']))

  purgePlugin = controller.RecordPurgePlugin(cherrypy.engine)
  purgePlugin.subscribe()
  cherrypy.engine.subscribe('exit', purgePlugin.unsubscribe)

  for item in apps + [purgePlugin]:
    item.storage = storageObj

