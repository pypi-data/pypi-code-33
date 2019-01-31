#! /usr/bin/env python

from __future__ import print_function
import numpy as np
from scipy.optimize import curve_fit
from pylab import *
import ROOT

# Test curve_fit, `curve_fit <https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html>`_

sigmay = 0.1
xmin = 1.0
xmax = 3.0

a_true = 10.0
b_true = 3.0

hPullA = ROOT.TH1F('hPullA', 'pull distribution for a', 100, -4., 4.)
hPullB = ROOT.TH1F('hPullB', 'pull distribution for b', 100, -4., 4.)

ROOT.gStyle.SetOptFit(11)

verbose = 0


def func(x, a, b):
    return a / x + b


for _ in range(1000):

    # wuerfele Daten
    xdata = np.arange(xmin, xmax, 0.1)
    ydata = np.random.normal(func(xdata, a_true, b_true), sigmay)
    ey = 0. * xdata + sigmay

    if verbose >= 2:
        print(xdata)
        print(ydata)
        print(ey)
    popt, pcov = curve_fit(func, xdata, ydata, sigma=ey, absolute_sigma=True, p0=[9.0, 2.0])
    a = popt[0]
    b = popt[1]
    ea = np.sqrt(np.diag(pcov)[0])
    eb = np.sqrt(np.diag(pcov)[1])

    if verbose >= 1:
        print('a = (%g +- %g), b = (%g +- %g)' % (a, ea, b, eb))

    pullA = (a - a_true) / ea
    pullB = (b - b_true) / eb
    hPullA.Fill(pullA)
    hPullB.Fill(pullB)

c = ROOT.TCanvas('cPull', 'pulls')
c.Divide(2, 1)
c.cd(1)
hPullA.Draw()
hPullA.Fit('gaus', 'L')
c.cd(2)
hPullB.Draw()
hPullB.Fit('gaus', 'L')

input()
