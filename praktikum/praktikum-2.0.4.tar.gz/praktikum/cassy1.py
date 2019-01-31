# -*- coding: utf-8 -*-

"""
Dieses Modul enthält die Funktion zum Einlesen von Daten, die mit einem
Cassy-1 System geschrieben wurden (Dateiendung .lab).
"""

import numpy as np

python_version = 2
try:
    import StringIO
except ImportError:
    python_version = 3
    import io

def lese_lab_datei(dateiname):
    '''
    LAB-Datei einlesen.

    :param dateiname: Name der einzulesenden Datei.
    :type dateiname: string
    :rtype: numpy-Array

    Aus dem zurückgegebenen numpy-Array erhält man
    über Array-Slicing die relevanten Datenreihen.

    Beispiel::

      from praktikum import cassy1
      data = cassy1.lese_lab_datei('lab/Pendel.lab')
      zeit = data[:,1]
      spannung = data[:,2]

    '''
    if python_version == 2:
        f = open(dateiname)
    else:
        f = io.open(dateiname, encoding = 'ISO-8859-1')
    dataSectionStarted = False
    dataSectionEnded = False
    data = ''
    # Messdaten werden anhand von Tabulatoren identifiziert.
    for line in f:
        if '\t' in line and not dataSectionEnded:
            data += line
            dataSectionStarted = True
        if not '\t' in line and dataSectionStarted:
            dataSectionEnded = True
    f.close()
    if python_version == 2:
        return np.genfromtxt(StringIO.StringIO(data))
    return np.genfromtxt(io.BytesIO(data.encode('ISO-8859-1')))

