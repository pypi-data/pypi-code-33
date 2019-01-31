# -*- coding: utf-8 -*-

"""
Dieses Modul enthält grundlegende Funktionen, die bei der Datenanalyse im Grundpraktikum Physik
verwendet werden.
"""

import numpy as np
from numpy import sqrt,sin,cos,log,exp
import scipy.fftpack
import scipy.odr


def lineare_regression(x,y,ey):
    '''
    Lineare Regression.

    :param x: x-Werte der Datenpunkte
    :type x: array_like
    :param y: y-Werte der Datenpunkte
    :type y: array_like
    :param ey: Fehler auf die y-Werte der Datenpunkte
    :type ey: array_like

    Diese Funktion benötigt als Argumente drei Listen:
    x-Werte, y-Werte sowie eine mit den Fehlern der y-Werte.
    Sie fittet eine Gerade an die Werte und gibt die
    Steigung a und y-Achsenverschiebung b mit Fehlern
    sowie das :math:`\chi^2` und die Korrelation von a und b aus.

    :rtype: Liste der Fit-Ergebnisse in der Reihenfolge [a, ea, b, eb, chiq, corr].

    '''

    s   = sum(1./ey**2)
    sx  = sum(x/ey**2)
    sy  = sum(y/ey**2)
    sxx = sum(x**2/ey**2)
    sxy = sum(x*y/ey**2)
    delta = s*sxx-sx*sx
    b   = (sxx*sy-sx*sxy)/delta
    a   = (s*sxy-sx*sy)/delta
    eb  = sqrt(sxx/delta)
    ea  = sqrt(s/delta)
    cov = -sx/delta
    corr = cov/(ea*eb)
    chiq  = sum(((y-(a*x+b))/ey)**2)

    return(a,ea,b,eb,chiq,corr)


def lineare_regression_xy(x,y,ex,ey):
    '''
    Lineare Regression mit Fehlern in x und y.

    :param x: x-Werte der Datenpunkte
    :type x:  array_like
    :param y: y-Werte der Datenpunkte
    :type y:  array_like
    :param ex: Fehler auf die x-Werte der Datenpunkte
    :type ex:  array_like
    :param ey: Fehler auf die y-Werte der Datenpunkte
    :type ey:  array_like
  
    Diese Funktion benötigt als Argumente vier Listen:
    x-Werte, y-Werte sowie jeweils eine mit den Fehlern der x-
    und y-Werte.
    Sie fittet eine Gerade an die Werte und gibt die
    Steigung a und y-Achsenverschiebung b mit Fehlern
    sowie das :math:`\chi^2` und die Korrelation von a und b aus.

    Die Funktion verwendet den ODR-Algorithmus von scipy.

    :rtype: Liste der Fit-Ergebnisse in der Reihenfolge [a, ea, b, eb, chiq, corr].

    '''
    a_ini,ea_ini,b_ini,eb_ini,chiq_ini,corr_ini = lineare_regression(x,y,ey)

    def f(B, x):
        return B[0]*x + B[1]

    model  = scipy.odr.Model(f)
    data   = scipy.odr.RealData(x, y, sx=ex, sy=ey)
    odr    = scipy.odr.ODR(data, model, beta0=[a_ini, b_ini])
    output = odr.run()
    ndof = len(x)-2
    chiq = output.res_var*ndof
    corr = output.cov_beta[0,1]/np.sqrt(output.cov_beta[0,0]*output.cov_beta[1,1])

    # Es scheint, dass die sd_beta von ODR auf ein chi2/dof=1 reskaliert werden. Deshalb nehmen
    # wir den Fehler direkt aus der Kovarianzmatrix.
    return output.beta[0], np.sqrt(output.cov_beta[0,0]), output.beta[1], np.sqrt(output.cov_beta[1,1]), chiq, corr

def fourier(t,y):
    '''
    Fourier-Transformation.

    :param t: Zeitwerte der Datenpunkte
    :type t: array_like
    :param y: y-Werte der Datenpunkte
    :type y: array_like

    :rtype: Gibt das Fourierspektrum in Form zweier Listen (freq,amp) \
    zurück, die die Fourieramplituden als Funktion der zugehörigen \
    Frequenzen enthalten.
    '''

    dt = (t[-1]-t[0])/(len(t)-1)
    fmax = 0.5/dt
    step = fmax/len(t)
    freq=np.arange(0.,fmax,2.*step)
    amp = np.zeros(len(freq))
    i=0
    for f in freq:
        omega=2.*np.pi*f
        sc = sum(y*cos(omega*t))/len(t)
        ss = sum(y*sin(omega*t))/len(t)
        amp[i] = sqrt(sc**2+ss**2)
        i+=1
    return (freq,amp)


def fourier_fft(t,y):
    '''
    Schnelle Fourier-Transformation.

    :param t: Zeitwerte der Datenpunkte
    :type t: array_like
    :param y: y-Werte der Datenpunkte
    :type y: array_like

    :rtype: Gibt das Fourierspektrum in Form zweier Listen (freq,amp) \
    zurück, die die Fourieramplituden als Funktion der zugehörigen \
    Frequenzen enthalten.
    '''

    dt = (t[-1]-t[0])/(len(t)-1)
    amp = abs(scipy.fftpack.fft(y))
    freq = scipy.fftpack.fftfreq(t.size,dt)
    return (freq,amp)


def exp_einhuellende(t,y,ey,sens=0.1):
    '''
    Exponentielle Einhüllende.

    :param t: Zeitwerte der Datenpunkte
    :type t: array_like
    :param y: y-Werte der Datenpunkte
    :type y: array_like
    :param ey:
    :type ey: array_like
        Fehler auf die y-Werte der Datenpunkte
    :param sens: Sensitivität, Wert zwischen 0 und 1
    :type sens: float, optional

    Die Funktion gibt auf der Basis der drei Argumente (Listen
    mit t- bzw. dazugehörigen y-Werten plus y-Fehler) der Kurve die
    Parameter A0 und delta samt Fehlern der Einhüllenden von der Form
    :math:`A=A_0\exp(-\delta{}t)` (abfallende Exponentialfunktion) als Liste aus.
    Optional kann eine Sensitivität angegeben werden, die bestimmt,
    bis zu welchem Prozentsatz des höchsten Peaks der Kurve
    noch Peaks für die Berechnung berücksichtigt werden
    (voreingestellt: 10%).

    :rtype: Liste [A0, sigmaA0, delta, sigmaDelta]

    '''
    if not 0.<sens<1.:
        raise ValueError(u'Sensitivität muss zwischen 0 und 1 liegen!')

    # Erstelle Liste mit ALLEN Peaks der Kurve
    Peaks=[]
    PeakZeiten=[]
    PeakFehler=[]
    GutePeaks=[]
    GutePeakZeiten=[]
    GutePeakFehler=[]
    if y[0]>y[1]:
        Peaks.append(y[0])
        PeakZeiten.append(t[0])
        PeakFehler.append(ey[0])
    for i in range(1,len(t)-1):
        if y[i] >= y[i+1] and \
           y[i] >= y[i-1] and \
           ( len(Peaks)==0 or y[i] != Peaks[-1] ): # handle case "plateau on top of peak"
           Peaks.append(y[i])
           PeakZeiten.append(t[i])
           PeakFehler.append(ey[i])

    # Lösche alle Elemente die unter der Sensitivitätsschwelle liegen
    Schwelle=max(Peaks)*sens
    for i in range(0,len(Peaks)):
        if Peaks[i] > Schwelle:
            GutePeaks.append(Peaks[i])
            GutePeakZeiten.append(PeakZeiten[i])
            GutePeakFehler.append(PeakFehler[i])

    # Transformiere das Problem in ein lineares
    PeaksLogarithmiert = log(np.array(GutePeaks))
    FortgepflanzteFehler = np.array(GutePeakFehler) / np.array(GutePeaks)
    LR = lineare_regression(np.array(GutePeakZeiten),PeaksLogarithmiert,FortgepflanzteFehler)

    A0=exp(LR[2])
    sigmaA0=LR[3]*exp(LR[2])
    delta=-LR[0]
    sigmaDelta=LR[1]
    return(A0,sigmaA0,delta,sigmaDelta)

def untermenge_daten(x,y,x0,x1):
    '''
    Extrahiere kleinere Datensätze aus (x,y), so dass x0 <= x <= x1

    :param x: x-Werte des Eingangsdatensatzes
    :type x: array_like
    :param y: Zugehörige y-Werte.
    :type y: array_like
    :param x0: x-Wert, ab dem die Daten extrahiert werden sollen.
    :type x0: float
    :param x1: x-Wert, bis zu dem die Daten extrahiert werden sollen.
    :type x1: float

    :rtype: (xn,yn) wobei xn und yn die reduzierten x- und y-Listen sind.
    '''
    xn=[]
    yn=[]
    for i,v in enumerate(x):
        if x0<=v<=x1:
            xn.append(x[i])
            yn.append(y[i])

    return (np.array(xn),np.array(yn))

def peak(x,y,x0,x1):
    '''
    Approximiere ein lokales Maximum in den Daten (x,y) zwischen x0 und x1.

    :param x: x-Werte des Eingangsdatensatzes
    :type x: array_like
    :param y: Zugehörige y-Werte.
    :type y: array_like
    :param x0: Untergrenze für die Lages des Maximums
    :type x0: float
    :param x1: Obergrenze für die Lages des Maximums
    :type x1: float

    :rtype: Approximierte Lage des Maximums entlang x.
    '''
    N = len(x)
    i1 = 0
    i2 = N-1
    for i in range(N):
       if x[i]>=x0:
         i1=i
         break
    for i in range(N):
       if x[i]>x1:
         i2=i
         break

    sum_y   = sum(y[i1:i2])
    sum_xy  = sum(x[i1:i2]*y[i1:i2])
    xm = sum_xy/sum_y
    return xm

def peakfinder_schwerpunkt(x,y):
    '''
    Finde Peak in den Daten (x,y) mit der Schwerpunktsmethode.

    :param x: x-Werte des Eingangsdatensatzes
    :type x: array_like
    :param y: Zugehörige y-Werte.
    :type y: array_like

    :rtype: Lage des Maximums entlang x.
    '''
    N = len(x)
    val = 1./sqrt(2.)
    i0=0
    i1=N-1
    ymax=max(y)
    for i in range(N):
        if y[i]>ymax*val:
            i0=i
            break
    for i in range(i0+1,N):
        if y[i]<ymax*val:
            i1=i
            break
    xpeak = peak(x,y,x[i0],x[i1])
    return xpeak


def gewichtetes_mittel(y,ey):
    '''
    Berechnet den gewichteten Mittelwert der gegebenen Daten.

    :param y: Datenpunkte
    :type y: array_like
    :param ey: Zugehörige Messunsicherheiten.
    :type ey: array_like

    :rtype: Gibt den gewichteten Mittelwert samt Fehler als Tupel (Mittelwert, Fehler) zurück.
    '''
    w = 1/ey**2
    s = sum(w*y)
    wsum = sum(w)
    xm = s/wsum
    sx = sqrt(1./wsum)

    return (xm,sx)


def mittelwert_stdabw(daten):
    '''
    Berechnet das arithmetische Mittel und die empirische Standardabweichung der gegebenen Daten.

    Der Mittelwert der Daten :math:`\{x_1, \ldots, x_N\}` ist definiert als
    :math:`\overline{x} = \sum\limits_{i=1}^N x_i`. Die Standardabweichung ist gegeben durch
    :math:`\sigma_x = \sqrt{\\frac{1}{N-1} \sum\limits_{i=1}^N (x_i-\\bar{x})^2}`.

    :param daten: Messwerte
    :type daten: array_like

    :rtype: Tupel (Mittelwert, Standardabweichung)
    '''

    return (np.mean(daten), np.std(daten, ddof=1))
