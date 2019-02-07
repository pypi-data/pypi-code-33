import numpy as np
from scipy.integrate import odeint
from osem.models.base import Model, tau_model


class HeatPump(Model):
    """
    Model class of a heat pump dynamic model based on a ratio of the theoretical COP of Carnot

    >>> hp = HeatPump(12E3, 10.0, 45.0)
    >>> hp.step(60)

    """
    #TODO DevMaster: need a clear name for the parameters the purpose is to be understood by everyone missing documentation

    def __init__(self, p_max, t_snk, t_src, n_th=0.4, tau=60.0, io_init=0.0, start="1/1/2000"):
        """
        This method instantiate the model for the heat pump.

        :param p_max: float - maximal heat production power in W
        :param t_snk: float - sink temperature (hot side) in deg.C
        :param t_src: float - source temperature (cold side) in deg.C
        :param n_th: float - ratio of the theoretical COP of Carnot
        :param tau: float - time constant of the heat pump
        :param io_init: float - initial setpoint for the load, must be between 0 and 1
        :param start: pandas.Timestamp - start time for simulation results
        """
        super().__init__(start)
        assert t_snk > t_src

        self.p_max = p_max
        self.t_src = t_src
        self.t_snk = t_snk

        self.n_th = n_th
        self.tau = tau

        self.io = io_init

        self.cop = self.n_th * ((self.t_snk + 273.15) / (self.t_snk - self.t_src))

        self.p_sink = self.io * self.p_max
        self.p_elec = self.p_sink / self.cop
        self.p_srce = self.p_sink - self.p_elec

    def step(self, step, unit="seconds"):
        """
        This method makes the model go one step in time.

        :param step: float - time step to simulate
        :param unit: string - unit of the time step
        """
        super().step(step, unit)

        t = np.arange(start=0, stop=step * self.UNIT[unit], step=1.0)

        res_p_sink = odeint(tau_model, self.p_sink, t, args=(self.io, self.tau, self.p_max))

        self.cop = self.n_th * ((self.t_snk + 273.15) / (self.t_snk - self.t_src))

        self.p_sink = round(res_p_sink[-1][0])
        self.p_elec = self.p_sink / self.cop
        self.p_srce = self.p_sink - self.p_elec
