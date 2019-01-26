'''Module provides CherryPy application which serves ChronologerUI.'''


import os

import cherrypy


class Ui:

  default = cherrypy.tools.staticdir.handler(  # @UndefinedVariable
    '/', 'static', root = os.path.dirname(__file__), index = 'index.html')

