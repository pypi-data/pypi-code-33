#! /usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
from praktikum import cassy

from pylab import *

argparser = argparse.ArgumentParser(description='Schnellauftragung zweier Datenreihen zu einer in einer Cassy-Datei gespeicherten Messung.')
argparser.add_argument('datei', default='', help='Name der Cassy-Datei (Dateityp lab, labx oder txt).')
argparser.add_argument('x', default='', help='Name der Datenreihe zur Auftragung auf der x-Achse.')
argparser.add_argument('y', default='', help='Name der Datenreihe zur Auftragung auf der y-Achse.')
argparser.add_argument('-m', '--messung', default=1, type=int, help='Nummer der gewünschten Messung.')
args = argparser.parse_args()

data = cassy.CassyDaten(args.datei)
messung = data.messung(args.messung)
x = messung.datenreihe(args.x)
y = messung.datenreihe(args.y)

figure()
errorbar(x.werte, y.werte, fmt='.')
xstr = x.symbol
if x.einheit:
    xstr += ' / %s' % x.einheit
ystr = y.symbol
if y.einheit:
    ystr += ' / %s' % y.einheit
xlabel(xstr)
ylabel(ystr)
show()
