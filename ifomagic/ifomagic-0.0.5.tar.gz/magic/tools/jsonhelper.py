'''
Helper functions to ensure JSON compliance.

MAGIC
@author: Isobel
'''
import numpy as np
import json


# To be used before saving dictionary in HDF5
def ensureSerializable(data):

   # First deal with single values : 0th-order type
   if data is None or isinstance(data, (bool, int, float, str)):
      return data

   # Now deal with lists and arrays : 1st-order type
   if isinstance(data, list):
      return [ensureSerializable(dat) for dat in data]

   if isinstance(data, np.ndarray):
      # First check whether array is complex
      if np.iscomplex(data).any():
         return {
            'complex numpy.ndarray' : {
               'real' : ensureSerializable(np.real(data).tolist()),
               'imag' : ensureSerializable(np.imag(data).tolist())
            }
         }

      return {
         'numpy.ndarray' : {
            'values' : ensureSerializable(data.tolist()),
            'dtype' : str(data.dtype)
         }
      }

   # Penultimately deal with dicts: 2nd-order type
   if isinstance(data, dict):
      return {key : ensureSerializable(val) \
              for key, val in data.items()}

   # Now deal with complicated, MAGIC-defined types
   if 'magic.materials' in str(data):
      # Data must be a materials class, so give its name and attributes
      return {str(data) : ensureSerializable(val) \
              for key, val in data.__dict__.items()}

   # Else return prompt to define new way of ensuring JSON compliance
   raise TypeError('''
      Type {t} not yet serializable! Help MAGIC by defining this yourself.
      '''.format(t=type(data)))


def toJSON(data):
   return json.dumps(ensureSerializable(data), sort_keys=True)


# To be used before passing dictionary from HDF5 to ifo model
# TODO - make this so that parameters can be loaded to update ifo
def ensureReadable(data):
   params = json.loads(data)

def fromJSON(data):
   ensureReadable(data)
   return data