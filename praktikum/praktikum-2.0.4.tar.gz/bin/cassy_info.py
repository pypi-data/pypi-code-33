#! /usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
from praktikum import cassy

argparser = argparse.ArgumentParser(description='Drucke eine Zusammenfassung der in einer Cassy-Datei enthaltenen Messungen.')
argparser.add_argument('datei', default='', help='Name der Cassy-Datei (Dateityp lab, labx oder txt).')
argparser.add_argument('-w', '--werte', default=False, action='store_true', help='Auch die Messwerte für alle Datenreihen ausgeben.')
args = argparser.parse_args()

data = cassy.CassyDaten(args.datei)
for m in range(1, data.anzahl_messungen()+1):
    print('')
    messung = data.messung(m)
    messung.info()
    for dr in messung.datenreihen:
        dr.info()
        if args.werte:
            print('Messwerte:')
            print(dr.werte)
