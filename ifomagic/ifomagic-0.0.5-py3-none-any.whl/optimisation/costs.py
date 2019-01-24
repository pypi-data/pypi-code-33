"""
Costs for optimisation parameters

References:
--- [1] - 

MAGIC
@author: Roshni
"""


# Cost and complexity functions are guides, can be altered
def getCost(ifo):
    p_hi = 200
    powerCost = 47e3+25e6*(ifo.parameters['power']/p_hi)**2
    totalCost = powerCost
    return totalCost

def getComplexity(ifo):
    # -1 here due to *
    upperLimit = ifo.limits['complexity'] -1
    Z_pow = ifo.parameters['power']/15
    Z_src = 1e-8/(ifo.parameters['srm_transmittance'])**2
    Z_itm = 1e-8/(ifo.parameters['itm_transmittance'])**2
    Z_total = Z_itm + Z_src
    complexity = upperLimit - Z_total
    # If complexity beyond limit, divide by it
    # *-1 here to avoid dividing by fraction and making distance greater
    if complexity <= -1:
        return abs(complexity)
    else:
        return 1