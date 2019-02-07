import numpy as np
from scipy.integrate import odeint
from thermo.chemical import Chemical
from osem.models.base import Model

#TODO DevMaster: need a clear name for the parameters the purpose is to be understood by everyone missing documentation
class Bath(Model):
    def __init__(self, vol, area, k=200.0, t_bath_init=50.0, fluid="water", start="1/1/2000"):
        super().__init__(start)
        self.vol = vol  # [m3]
        #TODO DevMaster: let's use self.area = area  no uppercase please
        self.A = area  # [m2]
        self.k = k  # [W/m2/K]
        self.fluid = Chemical(fluid)
        self.fluid.T = t_bath_init

        self.t_bath = t_bath_init

        self.p_heat = 0.0  # [W]
        self.m_dot_fresh = 0.02 * vol / 3600 * self.fluid.rho  # [kg/s]
        self.t_fresh = 12.0
        self.t_amb = 20.0

    def model(self, y, time):
        dydt = self.p_heat - self.k * self.A * (y - self.t_amb) - self.m_dot_fresh * self.fluid.Cp * (y - self.t_fresh)
        dydt /= self.vol * self.fluid.rho * self.fluid.Cp
        return dydt

    def step(self, step, unit="seconds"):
        super().step(step, unit)

        self.fluid.T = self.t_bath + 273.15

        t = np.arange(start=0, stop=step * self.UNIT[unit], step=1.0)

        res = odeint(self.model, self.t_bath, t)
        self.t_bath = res[-1][0]
