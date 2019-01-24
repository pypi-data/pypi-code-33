'''
Calculates integrand for use in Voyager noises carrier density and thermorefractive.

MAGIC
@author: Isobel
'''
import numpy as np 

def calculate(k, om, D, w_itm):
    return D*pow(k, 3)*np.exp(-pow(k, 2)*pow(w_itm, 2)/4)/\
              (pow(D, 2)*pow(k, 4) + pow(om, 2))