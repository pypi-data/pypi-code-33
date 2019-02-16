import decimal
import math
import random

import numpy
import numpy.random as nrand
import scipy.linalg

from funhandler.stochastic.generators import (geometric_brownian_motion_jump_diffusion_levels,
                                              geometric_brownian_motion_levels,
                                              heston_model_levels)
from funhandler.stochastic.helper import ModelParameters
from crayons import (blue, cyan, green, magenta, red, white, yellow)
# import matplotlib.pyplot as plt


# jump_diffusion_examples = []
# for i in range(paths):
#     jump_diffusion_examples.append(
#         geometric_brownian_motion_jump_diffusion_levels(mp))


# stochastic_volatility_examples = []
# for i in range(paths):
#     stochastic_volatility_examples.append(heston_model_levels(mp)[0])


# geometric_brownian_motion_examples = []
# for i in range(paths):
#     geometric_brownian_motion_examples.append(
#         geometric_brownian_motion_levels(mp))



class StochasticGenerator(object):
    def __init__(self):
        self.available_types = ["GBM", "HESTON", "MERTON"]
        self.rates_of_time = {
            "22mins": round(1 / 23893.94, 4),
            "37mins": round(1 / 14207.21, 4),
            "46mins": round(1 / 11427.54, 4),
            "hourly": round(1 / 8761.11, 4),
            "daily": round(1 / 365, 4),
            "monthly": round(1 / 12, 4)
        }
        self.mp = ModelParameters(
            all_s0=1000,
            all_r0=0.5,
            all_time=800,
            all_delta=0.00396825396,
            all_sigma=0.125,
            gbm_mu=-0.5,
            jumps_lamda=0.00125,
            jumps_sigma=0.001,
            jumps_mu=-0.2,
            cir_a=3.0,
            cir_mu=0.5,
            cir_rho=0.5,
            ou_a=3.0,
            ou_mu=0.5,
            heston_a=0.25,
            heston_mu=0.35,
            heston_vol0=0.06125)

    def generate(self, steps, start_price=1000,
                 interest_rate=0.5, rate_of_time="monthly",
                 _type="GBM", paths=15):
        """Generate a number of """
        print(
            f"{white('Were generating', bold=True)} a {red(_type, bold=True)} stochastic process with {yellow(steps, bold=True)} steps ... {magenta(interest_rate, bold=True)}"
        )
        assert isinstance(_type, str)
        assert (isinstance(steps, int) or isinstance(steps, float))
        assert (_type.upper() in self.available_types)
        assert (rate_of_time in list(self.rates_of_time.keys()))
        assert (isinstance(start_price, int) or isinstance(start_price, float))
        self.mp.set_time(steps)
        self.mp.set_start_price(start_price)
        self.mp.set_gbm_trend(interest_rate)

        if _type.upper() == "GBM":
            geometric_brownian_motion_samples = []
            m = geometric_brownian_motion_levels(self.mp)
            return m
        elif _type.upper() == "HESTON":
            stochastic_volatility_examples = []
            m = heston_model_levels(self.mp)[0]
            return m
        elif _type.upper() == "MERTON":
            jump_diffusion_examples = []
            m = geometric_brownian_motion_jump_diffusion_levels(self.mp)
            return m


# stoch = StochasticGenerator()
# gbm = stoch.generate(1000, start_price=10, _type="HESTON")
# print(gbm)