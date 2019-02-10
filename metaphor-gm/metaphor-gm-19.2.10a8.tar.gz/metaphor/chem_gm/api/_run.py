'''
Created on 12 avr. 2018

@author: jeanluc
'''

from functools import  reduce   
from ..chem_gm.components.gmmEngine import createGMModel

def get_model(modelfile, moleculename="", smiles=""):
    """Creation of a graphmachine model from a model file.
    parameters:
     - modelfile -> file created at the end of the training process (extensions may be 'nnx' or 'gmx').
     - moleculename -> name of the molecule you want to apply the model to. Optional parameter.
     - smiles -> smiles code of the molecule you want to apply the model to. Mandatory parameter.
    Return the created graphmachine model, or None if impossible.
    The model has many interesting properties:
     - propertyName -> Name of the current property
     - modelName -> Name of the model
     - weights -> Current weight vector
     - baselen -> Length of the training base
     - dispersionMatrix -> Current dispersion matrix
     - extraCount -> Number of side models included
     - inputCount -> Number of inputs
     - paramCount -> Number of weights
    """
    if not smiles:
        return None
    model = createGMModel(modelfile, moleculename, smiles)
    return model

def get_result(model, inputs=None, level=0):
    """Obtain the result of graphmachine model transfer function.
    parameters:
     - model -> model obtained with 'get_model' function.
     - inputs -> vector of inputs values. May be None
     - level -> level of the required transfer :
         - 0 -> return the best approximation of the required result
         - 1 -> return absolute minimum value, best value, absolute maximum value
         - 2 -> return list of minimum, value, maximum for each extra model
    """
    outs, CIps, CIms, levs = model.transferEx(inputs, withCI=2)
    outs = [float(val) for val in outs]
    CIps = [float(val) for val in CIps]
    CIms = [float(val) for val in CIms]
    levs = [float(val) for val in levs]
    outmean = reduce(lambda x, y: x + y, outs) / float(len(outs))
    if not level:
        return outmean
    if level == 1:
        return min(CIms), outmean, max(CIps)
    
    return outs, CIms, CIps, levs

if __name__ == '__main__':
    import sys, os
    curfile = __file__  # /Users/jeanluc/Documents/LiClipseWorkspace/Metaphor_gm/src/metaphor/chem_gm/api/run.py
    modelfile = os.path.join(os.path.dirname(__file__), "demofiles", "BJMA244_Test25_SM_20S_5N.nnx")
#     modelfile = '/Users/jeanluc/Documents/Workspace/GM_API/src/chem_gm/api/demofiles/BJMA244_Test25_SM_20S_5N.nnx'
    moleculename = "Hexane"
    smiles = 'C(C)CCCC'
    
    model = get_model(modelfile, moleculename, smiles)

#    ppty = model.propertyname
    print(model.modelName, model.propertyName)
    
# call with level 0
    print("mean best value:")
    value = get_result(model)
    
    print("\t{0:9.6f}".format(value))
    print()
    titles = ["min", "value", "max"]
    print("\t".join(titles))
    
# call with level 1    
    mini, val, maxi = get_result(model, level=1)
    
    values = ["{0:6.3f}".format(val) for val in [mini, val, maxi]]
    print("\t".join(values))
    print()
    print("available results")
    titles = ["value", "max", "min", "leverage"]
    print("\t".join(titles))
    
# call with level 2
    outs, CIps, CIms, levs = get_result(model, level=2)
    
    for out, CIp, CIm, lev in zip(outs, CIps, CIms, levs):
        res = ["{0:6.3f}".format(val) for val in [out, CIp, CIm, lev]]
        st = "\t".join(res)
        print(st)