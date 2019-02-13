# -*- coding: utf-8 -*-

"""Main module."""
from .fluid import Plasma

p = Plasma(Te0 = 2*u.eV, ne0 = 2e15*u.m**(-3), L=5*u.cm, mi=40*u.Da, sigma=0.029e6*u.s**(-1), gamma=1  )
p.solve()
p.plotsummary()
