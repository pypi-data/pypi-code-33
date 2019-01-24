"""
Optimisation using scipy differential evolution function

RV TODO: ADD ref

MAGIC
@author: Roshni
"""
from magic import Calculator
from magic.optimisation import costs


# Differential evolution, x0 = array of optimising parameters, determined by no. bounds
def optimise(x0, signal, ifo, params, include_cost = True): 
  for i, k in enumerate(sorted(params)):
    params[k] = x0[i]
  ifo.reset_noise(parameters=params)
  if include_cost == True:
    ifo.costs['cost'] = costs.getCost(ifo)
    ifo.costs['complexity']  = costs.getComplexity(ifo)
  else:
      ifo.costs['complexity'] = 1
      ifo.costs['cost'] = 0
  if ifo.costs['cost']  > ifo.limits['budget']:
    distance = 0
  else:
    if signal['type'] == 'imr':
      distance = Calculator(ifo).calculateDetectorRange(signal['m1'], signal['m2'], full = True)
    elif signal['type'] == 'input':
      distance = Calculator(ifo).calcInputSignalRange(signal['strain'], signal['distance'])
    distance = -distance/ifo.costs['complexity'] 
  return distance

def output(ifo, params, result):
  output = {}
  for i, k in enumerate(sorted(params)):
    output[k] = result['x'][i]
  output['cost'] = ifo.costs['cost']
  output['complexity'] = ifo.costs['complexity']
  output['Optimised Distance'] = -result['fun']*ifo.costs['complexity']
  print(output)
  return ifo