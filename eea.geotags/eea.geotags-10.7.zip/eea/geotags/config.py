""" Configure
"""
from zope.i18nmessageid import MessageFactory
_ = MessageFactory("eea")

PROJECTNAME = 'eea.geotags'
ADD_CONTENT_PERMISSION = "Add portal content"

# See http://geonames.org
WEBSERVICE = 'http://api.geonames.org/searchJSON'
ANNO_TAGS = 'eea.geotags.tags'
