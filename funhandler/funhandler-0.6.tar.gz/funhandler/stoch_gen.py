import numba
import numpy as np
from crayons import (blue, cyan, green,
                    magenta, red, white, yellow)


class ModelParameters:
    """
    Encapsulates model parameters
    """

    def __init__(self,
                 all_s0,
                 all_time,
                 all_delta,
                 all_sigma,
                 gbm_mu,
                 jumps_lamda=0.0,
                 jumps_sigma=0.0,
                 jumps_mu=0.0,
                 cir_a=0.0,
                 cir_mu=0.0,
                 all_r0=0.0,
                 cir_rho=0.0,
                 ou_a=0.0,
                 ou_mu=0.0,
                 heston_a=0.0,
                 heston_mu=0.0,
                 heston_vol0=0.0):
        # This is the starting asset value
        self.all_s0 = all_s0
        # This is the amount of time to simulate for
        self.all_time = all_time
        # This is the delta, the rate of time e.g. 1/252 = daily, 1/12 = monthly
        self.all_delta = all_delta
        # This is the volatility of the stochastic processes
        self.all_sigma = all_sigma
        # This is the annual drift factor for geometric brownian motion
        self.gbm_mu = gbm_mu
        # This is the probability of a jump happening at each point in time
        self.lamda = jumps_lamda
        # This is the volatility of the jump size
        self.jumps_sigma = jumps_sigma
        # This is the average jump size
        self.jumps_mu = jumps_mu
        # This is the rate of mean reversion for Cox Ingersoll Ross
        self.cir_a = cir_a
        # This is the long run average interest rate for Cox Ingersoll Ross
        self.cir_mu = cir_mu
        # This is the starting interest rate value
        self.all_r0 = all_r0
        # This is the correlation between the wiener processes of the Heston model
        self.cir_rho = cir_rho
        # This is the rate of mean reversion for Ornstein Uhlenbeck
        self.ou_a = ou_a
        # This is the long run average interest rate for Ornstein Uhlenbeck
        self.ou_mu = ou_mu
        # This is the rate of mean reversion for volatility in the Heston model
        self.heston_a = heston_a
        # This is the long run average volatility for the Heston model
        self.heston_mu = heston_mu
        # This is the starting volatility value for the Heston model
        self.heston_vol0 = heston_vol0

    def set_time(self, _time):
        self.all_time = _time

    def set_start_price(self, price):
        self.all_s0 = price

    def set_jump_size(self, size):
        pass

    def set_drift_factor(self):
        pass

    def set_jump_probability(self, prob):
        pass

    def set_start_hest_vol(self, vol):
        pass

    def set_avg_hest_vol(self, vol):
        pass




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
            gbm_mu=0.058,
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
            heston_vol0=0.06125
        )

    def generate(self, steps, start_price=1000, interest_rate=0.5, rate_of_time="hourly", _type="GBM", paths=15):
        """Generate a number of """
        print(
            f"{white('Were generating', bold=True)} a {red(_type, bold=True)} stochastic process with {yellow(steps, bold=True)} steps"
        )
        assert isinstance(_type, str)
        assert (isinstance(steps, int) or isinstance(steps, float))
        assert (_type.upper() in self.available_types)
        assert (rate_of_time in list(self.rates_of_time.keys()))
        assert (isinstance(start_price, int) or isinstance(start_price, float))
        self.mp.set_time(steps)
        self.mp.set_start_price(start_price)




stoch_gene = StochasticGenerator()
stoch_gene.generate(10000.0, _type="GBM", rate_of_time="hourly")
