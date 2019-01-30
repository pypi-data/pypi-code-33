import math
import extractTool # used for the the transformation and prints  # used for the the transformation and prints
import click        # used to print something 
import os

"""
Function for calling up all important fuctions 
:returns: similarity score of two geospatial files
"""
def master(bbox1, bbox2, type1, type2):
    try:
        sim = calculatedScore(bbox1, bbox2)
        score = whatDataType(type1, type2, sim)
        return score

    except Exception:
        if bbox1 == None or bbox2 == None:
            print("One of the Bounding Boxes are Empty")
            score = 0
            return score

"""
Function to apply data type similarity on the similarity score

:param input1: filepath from a file
:param input2: filepath from a file
:param sim: spatial similarity score of two bounding boxes including the similarity of the data type
"""
def whatDataType(type1, type2, sim):  
    input1 = extension(type1)
    input2 = extension(type2)
    if input1 == "raster" and input2 == "raster":
        return sim
    if input1 == "vector" and input2 == "vector":
        return sim
    if input1 == "raster" and input2 == "vector" or input1 == "vector" and input2 == "raster":
        sim = sim*5/4
        if sim > 1:
            sim = 1
        return sim
    else: 
        return sim

"""
Function to find out if the datafile is a vector or rasta datatype

:param filepath: Path to the file
:returns: String containing vector or raster
"""
def extension(typ):
    if typ == "csv" or typ == "tif" or typ == "gpkg":
        return "raster"
    if typ == "geojson" or typ == "shp" or typ == "gml" or typ == "kml" or typ == "nc":
        return "vector"
    else:
        print("not valid")
        return None

"""
Function to calculate the similarity score based on the spatial similarity
for a more detailed explanation look at: https://github.com/carobro/Geosoftware2/blob/master/Informationen_Allgemein/SimilarityCalculation.md#%C3%A4hnlichkeitsberechnung-version-2

:param bbox1: Bounding Box from a file
:param bbox2: Bounding Box from a file
:returns: similarity score from the two Bounding Boxes
"""
def calculatedScore(bbox1,bbox2):
    if isinstance(bbox1[0], float) and isinstance(bbox1[1], float) and isinstance(bbox1[2], float) and isinstance(bbox1[3], float) and isinstance(bbox2[0], float) and isinstance(bbox2[1], float) and isinstance(bbox2[2], float) and isinstance(bbox2[3], float):
        if  bbox1[0] != bbox2[0] and bbox1[1] != bbox2[1] and bbox1[2] != bbox2[2] and bbox1[3] != bbox2[3]: 
            if distance(bbox1,bbox2) < 20000:
                simdis = distance(bbox1,bbox2)/20000
            else:
                simdis = 1
            if abs(area(bbox1) - area(bbox2)) < 1000000:
                simA = (abs(area(bbox1) - area(bbox2)))/1000000
            else:
                simA = 1
            sim = (2 * simdis + simA)/3
            return sim
        else:
            sim = 0
            return sim
    else:
        sim = 1
        return sim

"""
Function to calculate the mean latitude

:param bbox: bounding box of a file with the format: ['minlon', 'minlat', 'maxlon', 'maxlat']
:returns: the mean Latitude
"""
def meanLatitude (bbox):
    lat = (bbox[3]+bbox[1])/2
    return lat

"""
Function to calculate the mean longitude

:param bbox: bounding box of a file with the format: ['minlon', 'minlat', 'maxlon', 'maxlat']
:returns: the mean Longitude
"""

def meanLongitude (bbox):
    lon = (bbox[2]+bbox[0])/2
    return lon

"""
Function to calculate the width of the bounding box

:param bbox: bounding box of a file with the format: ['minlon', 'minlat', 'maxlon', 'maxlat']
:returns: the mean width of the bounding box (in km)
"""
def width (bbox):
    x = (bbox[2]-bbox[0])*111.3 * (math.cos(meanLatitude(bbox)*math.pi/180))
    return x

"""
Function to calculate the length of the bounding box

:param bbox: bounding box of a file with the format: ['minlon', 'minlat', 'maxlon', 'maxlat']
:returns: the length of the bounding box (in km)
"""
def length (bbox):
    y =(bbox[3]-bbox[1])*111.3
    return y

"""
Function to calculate the area of the bounding box

:param bbox: bounding box of a file with the format: ['minlon', 'minlat', 'maxlon', 'maxlat']
:returns: the area square kilometre
"""
def area (bbox):
    A = width(bbox) * length(bbox)
    return A

"""
auxiliary calculation https://en.wikipedia.org/wiki/Law_of_cosines

:param bbox1: Bounding Box from a file
:param bbox2: Bounding Box from a file
:returns: the cosinus
"""
def lawOfCosines(bbox1,bbox2):
    cos = math.sin((meanLatitude(bbox1) * math.pi/180))*math.sin((meanLatitude(bbox2)*math.pi/180)) + math.cos((meanLatitude(bbox1)*math.pi/180)) * math.cos((meanLatitude(bbox2)*math.pi/180)) * math.cos((meanLongitude(bbox1)*math.pi/180)-(meanLongitude(bbox2)*math.pi/180))
    return cos

"""
function to calculate the distace between two Bounding Boxes

:param bbox1: Bounding Box from a file
:param bbox2: Bounding Box from a file
:returns: the distance
"""
def distance(bbox1,bbox2):
    dist = math.acos(lawOfCosines(bbox1,bbox2)) * 6378.388
    return dist