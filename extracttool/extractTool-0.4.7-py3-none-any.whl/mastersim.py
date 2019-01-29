import math
import extractTool
import getShapefileInfo, getGeoTiffInfo, getCSVInfo, getGeoJsonInfo, getNetCDFInfo, getGeoPackageInfo, getIsoInfo, openFolder
import similar
import click
import os

"""
Function for calling up all important fuctions 

:param filepath1: filepath from a file
:param filepath2: filepath from a file
:returns: similarity score of two geospatial files
"""
def master(filepath1, filepath2):
    print(filepath1)
    print(filepath2)
    first = extractTool.getMetadata(filepath1, 'bbox', 'single', True)
    second = extractTool.getMetadata(filepath2, 'bbox', 'single', True)
    try:
        print('___________________________________')
        bbox1 = first[0]
        bbox2 = second[0]
        print("Boudning Box filepath1")
        print(bbox1)
        print("Boudning Box filepath2") 
        print(bbox2)
        print('____________________________________')
        sim = similar.calculatedScore(bbox1, bbox2)
        print("Calculed Bounding Box similarity:")
        print(sim)
        print('____________________________________')
        score = similar.whatDataType(filepath1, filepath2, sim)
        print('____________________________________')
        print("Final similarity score")
        print(score)
        print('____________________________________')
        return score

    except Exception:
        if first == None or second == None:
            print("One of the Bounding Boxes are Empty")
            score = 1
            print(score)
            return score

  