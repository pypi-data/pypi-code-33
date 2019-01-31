#! /usr/bin/env python

from praktikum import analyse
import numpy as np
from pylab import *
import ROOT

sigmax = 0.5
sigmay = 1.0
xmin =  -10.
xmax =  30.

a_true = 0.5
b_true = 3.0

hPullA = ROOT.TH1F('hPullA','pull distribution for a (slope)',  100, -4., 4.)
hPullB = ROOT.TH1F('hPullB','pull distribution for b (offset)', 100, -4., 4.)

ROOT.gStyle.SetOptFit(11)

for _ in range(1000):

    # wuerfele Daten
    x = np.arange(xmin,xmax)
    xdata = np.random.normal(x,sigmax)
    ydata = np.random.normal(a_true*x+b_true,sigmay)
    ex = 0.*x+sigmax
    ey = 0.*x+sigmay

    # Aufruf der linearen Regression
    a,ea,b,eb,chiq,corr = \
        analyse.lineare_regression_xy(xdata,ydata,ex,ey)
    #print 'Ergebnis: a=%f+-%f, b=%f+-%f, chi2=%f, corr=%f' % (a,ea,b,eb,chiq,corr)

    pullA = (a-a_true)/ea
    pullB = (b-b_true)/eb
    hPullA.Fill(pullA)
    hPullB.Fill(pullB)

c = ROOT.TCanvas('cPull','pulls')
c.Divide(2,1)
c.cd(1)
hPullA.Draw()
hPullA.Fit('gaus','L')
c.cd(2)
hPullB.Draw()
hPullB.Fit('gaus','L')

input()
