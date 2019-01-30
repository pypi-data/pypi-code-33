import math         # used for the computations
import extractTool  # used for the the transformation and prints
import similar      # used to calculate the similarity score
import click        # used to print something

"""
Function for calling up all important functions 

:param filepath1: filepath from a file
:param filepath2: filepath from a file
:returns: similarity score of two geospatial files
"""
def master(filepath1, filepath2):
    first = extractTool.getMetadata(filepath1, 'bbox' , True)
    second = extractTool.getMetadata(filepath2, 'bbox' , True)
    try:
        bbox1 = first[0]
        bbox2 = second[0]
        sim = similar.calculatedScore(bbox1, bbox2)
        score = similar.whatDataType(filepath1, filepath2, sim)
        return score

    except Exception:
        if first == None or second == None:
            print("One of the Bounding Boxes are Empty")
            score = 1
            return score