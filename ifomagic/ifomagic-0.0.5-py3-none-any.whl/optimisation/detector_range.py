"""
Calculate detector range

MAGIC
@author: Roshni
"""
from magic import Calculator

def calculate(signal, ifo):
  if signal['type'] == 'imr':
    distance = Calculator(ifo).calculateDetectorRange(signal['m1'], signal['m2'], full = True)
  elif signal['type'] == 'input':
    distance = Calculator(ifo).calcInputSignalRange(signal['strain'], signal['distance'])
  print("Initial maximum detector range:", distance, "Mpc with", str(ifo.__class__.__name__) )
  return distance