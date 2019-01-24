'''
Parent class for materials.

MAGIC
@author: Isobel
'''
import abc
from magic import constants


class MaterialParent(object):
   __metaclass__ = abc.ABCMeta

   @abc.abstractmethod
   def __init__(self, properties={}):

      UNSET = constants.UNSET

      self.properties = {}
      # First initialise essential properties as unset
      self.properties['rho'] = UNSET
      self.properties['C'] = UNSET
      self.properties['k'] = UNSET
      self.properties['alpha'] = UNSET
      self.properties['dlnE_dT'] = UNSET
      self.properties['phi'] = UNSET
      self.properties['Y'] = UNSET

      # Add to or overwrite with any user-defined properties
      self.updateProperties(properties)

   def updateProperties(self, properties):

      for key in properties:
         self.properties[key] = properties[key]