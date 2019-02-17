import uncertainties as uc
from uncertainties.umath import *

def erzeuge_var(name, value):
    globals()[name] = value

def calculate(var, value, error, formel):
    
    formel = formel[0]
    for i in range(len(var)):
        erzeuge_var(var[i], uc.ufloat(value[i], error[i]))
    
    try:
        ergebnis_all = eval(formel)
        ergebnis = '{:.5u}'.format(ergebnis_all)
    except:
        ergebnis = 'error'

    return ergebnis, formel

def part_abl(va, formel):
    from sympy import diff, sympify
    
    try:
        formel = sympify(formel)
        return [str(formel.diff(i)) for i in va]
    except TypeError:
        part_abl.append('error')
    
    print(part_abl)
        
    return part_abl
    
    
    
    
    
