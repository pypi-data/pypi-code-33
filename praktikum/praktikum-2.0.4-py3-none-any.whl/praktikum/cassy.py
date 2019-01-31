#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Dieses Modul enthält die Funktionalität zum Einlesen von Daten, die mit einem
Cassy-System geschrieben wurden (Dateiendungen .lab (Cassy-1), bzw. .labx oder
.txt (Cassy-2)).
"""

from __future__ import print_function
from builtins import range
from builtins import object

import numpy as np
import os
import re
import sys
import xml.etree.ElementTree as ET

class Datenreihe(object):
    """
    Eine Datenreihe enthält die Messwerte und weitere Informationen zu einer bestimmten
    bei einer Messung mit Cassy aufgezeichneten Größe.

    Die Variable *werte* enthält die Liste der Messwerte. Daneben werden das während der Messung
    mit Cassy verwendete Formelzeichen (*symbol*), eine Beschreibung der Messgröße (*groesse*) und
    die Einheit der Messwerte (*einheit*) zur Verfügung gestellt.

    .. py:attribute:: werte

       Numpy-Array, dass die während der Messung mit Cassy aufgezeichneten Messwerte enthält.

    .. py:attribute:: groesse

       Beschreibung der Messgröße (z.B. "Stromstärke").

    .. py:attribute:: symbol

       Für den Zugriff auf die Datenreihe zu verwendendes Symbol (z.B. "I_A1").

    .. py:attribute:: einheit

       Einheit der Messwerte in *werte* (z.B. "mA").

    """
    def __init__(self, werte, groesse, symbol, einheit):
        self.werte = werte
        self.groesse = groesse
        self.symbol = symbol
        self.einheit = einheit

    def info(self):
        """
        Gebe Messgröße, Symbol und Einheit der Datenreihe aus, ebenso wie Informationen zu den
        enthaltenen Messwerten (Anzahl, Minimum und Maximum).
        """
        infostring = u'%s %s' % (self.groesse, self.symbol)

        if self.einheit:
            infostring += u'/%s' % self.einheit

        if len(self.werte) == 0:
            infostring = u'%-40s (leer)' % infostring
        elif len(self.werte) == 1:
            infostring = u'%-40s 1 Wert: %g' % (infostring, self.werte[0])
        else:
            w_finite = self.werte[np.isfinite(self.werte)]
            n_invalid = len(self.werte) - len(w_finite)
            w_min = w_finite.min()
            w_max = w_finite.max()
            infostring = u'%-40s %d Werte von %g bis %g' % (infostring, len(self.werte) - n_invalid, w_min, w_max)
            if n_invalid:
                infostring += u' (und %d ungültige Werte)' % n_invalid

        try:
            print(infostring)
        except UnicodeEncodeError:
            print(infostring.encode('utf-8'))


class Messung(object):
    """
    Eine einzelne mit Cassy aufgezeichnete Messung.

    Für jede bei der Messung aufgezeichnete Größe wird eine :py:class:`Datenreihe` angelegt.

    Darüber hinaus werden der Zeitpunkt der Messung und der während der Messung in
    der Cassy-Software eingegebene Kommentar gespeichert. (Nur bei Verwendung der
    .labx-Dateien.)
    """
    def __init__(self, zeitpunkt, beschreibung, nummer):
        self.zeitpunkt = zeitpunkt
        self.beschreibung = beschreibung
        self.nummer = nummer
        self.datenreihen = [ ]

    def info(self):
        """
        Gebe Zeitpunkt und Kommentar zu der Messung aus (soweit vorhanden), sowie die Symbole
        aller in der Messung enthaltenen Datenreihen.
        """
        if self.zeitpunkt != 'leer':
            infostring = u'Messung #%d: %-40s    ' % (self.nummer, self.zeitpunkt)
            if self.beschreibung:
                infostring += u'"%s"' % self.beschreibung
        else:
            infostring = u'Messung #%d: ' % self.nummer
            
        datenstring = u', '.join([x.symbol for x in self.datenreihen])
        infostring += u' (Datenreihen: %s)' % datenstring
        try:
            print(infostring)
        except UnicodeEncodeError:
            print(infostring.encode('utf-8'))

    def datenreihe(self, symbol):
        """
        Zugriff auf die zum *symbol* gehörende :py:class:`Datenreihe`.

        :param symbol: Bei der Aufzeichnung mit Cassy verwendetes Symbol.
        :type symbol: string
        :rtype: :py:class:`Datenreihe`
        """
        for x in self.datenreihen:
            if x.symbol == symbol:
                return x
        raise RuntimeError('"%s" ist nicht in Messung #%d enthalten!' % (symbol, self.nummer))


class CassyDaten(object):
    """
    Stellt die Gesamtheit der aus einer Cassy2-Datei eingelesenen Daten zur Verfügung.

    Die Daten setzen sich aus einzelnen Messreihen (vom Typ :py:class:`Messung`) zusammen.

    :param cassydatei: Dateiname der einzulesenden Cassy-Datei (Dateiendung: .lab, .labx oder .txt)
    :type cassydatei: string
    """

    def __init__(self, cassydatei):
        """
        Konstruktor.

        :param cassydatei: Dateiname der einzulesenden Cassy-2 Datei (Dateiendung: .labx oder .txt)
        :type cassydatei: string
        """
        self.messungen = [ ]
        filetype = os.path.splitext(cassydatei)[1]
        if filetype == '.labx':
            self.parseXml(cassydatei)
        elif filetype == '.txt':
            self.parseTxt(cassydatei)
        elif filetype == '.lab':
            self.parseLab(cassydatei)
        else:
            raise RuntimeError('Cannot parse extension %s' % filetype)

    def info(self):
        """
        Gebe Informationen über die enthaltenen Messungen aus.
        """
        for m in self.messungen:
            m.info()

    def anzahl_messungen(self):
        """
        Anzahl der Messungen in der Datei.
        """
        return len(self.messungen)

    def messung(self, nummer):
        """
        Zugriff auf einzelne :py:class:`Messung`.

        :param nummer: Nummer der gewünschten Messung (1..N)
        :type nummer: int
        :rtype: :py:class:`Messung`
        """
        if nummer < 1 or nummer > len(self.messungen):
            raise ValueError(u'Ungültige Messung: #%d!' % nummer)
        return self.messungen[nummer-1]

    def parseXml(self, cassydatei):
        print('Lese CASSY-2 Datei: ', cassydatei)
        xmlp = ET.XMLParser(encoding='utf-8')
        tree = ET.parse(cassydatei, parser=xmlp)
        root = tree.getroot()
        number = 1 # Nummer der Messung ('Messreihe' in CASSY-2)
        channeldict = dict()
        for allchannels in root.findall('allchannels'):
            for channels in allchannels.findall('channels'):
                
                for channel in channels.findall('channel'):
                    datetime = channel.get('datetime')
                    description = channel.get('text')
                    if datetime:
                        self.messungen.append(Messung(datetime, description, number))
                        number += 1
                    quantity = channel.find('quantity').text
                    symbol = channel.find('symbol').text
                    unit = channel.find('unit').text
                    values = channel.find('values')
                    n_values = int(values.get('count'))
                    value_array = np.zeros(n_values)
                    i = 0
                    for value in values:
                        value_array[i] = np.float32(value.text)
                        i += 1

                    # suche korrekte Messung fuer diese Datenreihe
                    if symbol not in channeldict:
                        channeldict[symbol] = 0
                    messung_index = channeldict[symbol]
                    channeldict[symbol] += 1
                    self.messungen[messung_index].datenreihen.append(Datenreihe(value_array, quantity, symbol, unit))

    def parseTxt(self, cassydatei):
        print('Lese CASSY-2 Textdatei: ', cassydatei)
        messung_nummer = 0
        try:
            f = open(cassydatei, encoding='utf-8-sig')
        except TypeError:
            # python2
            f = open(cassydatei)

        for line in f:
            try:
                line = line.strip().decode('utf-8-sig')
            except AttributeError:
                # python3
                line = line.strip()
            if line.startswith('MIN='):
                continue
            if line.startswith('MAX='):
                continue
            if line.startswith('SCALE='):
                continue
            if line.startswith('DEC='):
                continue
            if line.startswith('DEF='):
                # neue Messung
                messung_nummer += 1
                messung = Messung('leer', 'leer', messung_nummer)
                self.messungen.append(messung)
                # Achtung: Einheit ist nicht immer vorhanden!
                for m in re.finditer(u'\"([\wäöüÄÖÜß]+)\" ([ /\w]+)', line):
                    quantity = m.group(1)
                    rest = m.group(2)
                    m2 = re.match(r'(\w+) / (\w+)', rest)
                    if m2:
                        symbol = m2.group(1)
                        unit = m2.group(2)
                    else:
                        symbol = rest.strip()
                        unit = ''
                    messung.datenreihen.append(Datenreihe([], quantity, symbol, unit))
                continue

            # Zeile mit Werten
            for v in enumerate(line.split()):
                value = np.float32(v[1].replace(',', '.'))
                messung.datenreihen[v[0]].werte.append(value)

        f.close()

        # Listen in numpy-Arrays umwandeln
        for m in self.messungen:
            for d in m.datenreihen:
                d.werte = np.array(d.werte)


    def parseLab(self, cassydatei):
        print('Lese CASSY-1 Textdatei: ', cassydatei)
        messung_nummer = 0
        try:
            f = open(cassydatei, encoding='ISO-8859-1')
        except TypeError:
            # python2
            f = open(cassydatei)
        lineCounter = 0
        lastIndex = 0

        quantities = [ ]
        symbols = [ ]
        units= [ ]


        isData = False
        for line in f:
            lineCounter += 1
            line = line.strip()
            if lineCounter <= 2:
                continue

            # Messdaten werden anhand von Tabulatoren identifiziert.
            if '\t' in line:
                werte_tokens = line.split()
                if werte_tokens.count('NAN') == len(werte_tokens):
                    continue
                try:
                    index = int(werte_tokens[0])
                    werte = [float(x) for x in werte_tokens]
                except ValueError:
                    continue

                isData = True

                if index != 1 and index != lastIndex + 1:
                    continue

                #print('Good data line: "%s"' % line)

                if index == 1:
                    # neue Messung
                    messung_nummer += 1
                    messung = Messung('leer', 'leer', messung_nummer)
                    for dr in zip(quantities, symbols, units):
                        # Es scheint, dass zu jeder Messgröße "Zeit" auch immer eine Messgröße "Frequenz" erstellt wird, aber ohne dass dieser Werte in den Datenzeilen entsprechen. 
                        if not (dr[0] == 'Frequenz' and dr[1] == 'f'):
                            messung.datenreihen.append(Datenreihe([], dr[0], dr[1], dr[2]))
                    self.messungen.append(messung)

                lastIndex = index

                for v in enumerate(werte_tokens):
                    messung.datenreihen[v[0]].werte.append(np.float32(v[1]))

                continue

            # Als erstes werden die Messgrößen im Header definiert.
            if not isData:

                # Zeilen mit Einstellungen (lange Zahlenreihen, einschließlich Messbereiche) werden übersprungen.
                # Teste, ob erstes Element der Zeile eine Zahl ist.
                try:
                    first_numbers = float(line.split(' ')[0])
                    continue
                except ValueError:
                    pass
                except IndexError:
                    pass

                #print('Good header line: "%s"' % line)

                # Neue Messgröße!
                if len(quantities) == len(units):
                    try:
                        # python2
                        quantities.append(line.decode('ISO-8859-1'))
                    except AttributeError:
                        # python3
                        quantities.append(line)
                    continue
                if len(symbols) < len(quantities):
                    try:
                        symbols.append(line.decode('ISO-8859-1'))
                    except AttributeError:
                        symbols.append(line)
                    continue
                if len(units) < len(symbols):
                    try:
                        units.append(line.decode('ISO-8859-1') if line else '')
                    except AttributeError:
                        units.append(line if line else '')
                    continue

                continue

        f.close()

        # Listen in numpy-Arrays umwandeln
        for m in self.messungen:
            for d in m.datenreihen:
                d.werte = np.array(d.werte)
