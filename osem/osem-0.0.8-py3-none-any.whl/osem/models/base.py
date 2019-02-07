import pandas as pd
import numpy as np

#TODO DevMaster: base is not so clear need a definition
#TODO DevMaster: for calculation helper keep it in an helper directory
def tau_model(y, t, io, tau, p_nom):
    """Define ODE for a simplified dynamic model using time constant"""
    dydt = (p_nom * io - y) / tau
    return dydt


def normalize(v, y_min=0.0, y_max=1.0, x_min=0, x_max=1):
    v = np.array([min(vx, x_max) for vx in v])
    v = np.array([max(vx, x_min) for vx in v])
    return (y_max - y_min) / (x_max - x_min) * (v - x_min)


class Model:
    #TODO DevMaster: What is the purpose of this class missing documentation
    UNIT = {"seconds": 1, "minutes": 60, "hours": 3600}

    def __init__(self, start):
        """"""
        self.time = pd.to_datetime(start)

    def step(self, step, unit):
        """"""
        self.time += pd.DateOffset(**{unit: step})
