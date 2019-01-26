# -*- coding: utf-8 -*-
"""
Created on Sat Jan 26 15:20:26 2019

@author: Uendel Rocha
"""

import sanitize

def getCoachData(fileName):
    try:
        with open(fileName, 'r') as coachFile:
            return([sanitize.sanitize(t) for t in coachFile.read().strip().split(',')])
    
    except IOError as ioerr:
        print("Erro ao abrir o arquivo " + fileName)
        print(str(ioerr))
        return(None)
