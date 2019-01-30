import similar # used to invoke the function for the similarity score
import os # used to get the location of the testdata

"""
These tests check if the calucated similar score from two Bouding Boxes
is equal to our manually calculated score
"""
#Germany - Poland
def test_germany_poand():
    bbox1 = [5.8663155, 47.270111, 15.041932 , 55.099159]
    bbox2 = [14.122971, 49.002048, 24.145782, 55.033695]
    assert similar.calculatedScore(bbox1, bbox2) == 0.052537198756258265

# Muenster - Greven
def test_muenster_greven():
    bbox1 = [7.473785, 51.840145, 7.774364, 52.060024]
    bbox2 = [7.5234, 52.0326, 7.7556, 52.152]
    assert similar.calculatedScore(bbox1, bbox2) == 0.0006267747993827629

# Germany - Muenster
def test_germany_muenster():
    bbox1 = [5.8663155, 47.270111, 15.041932 , 55.099159]
    bbox2 = [7.5234, 52.0326, 7.7556, 52.152]
    assert similar.calculatedScore(bbox1, bbox2) == 0.19316458780635867

# Germany - Mexico
def test_germany_mexico():
    bbox1 = [5.8663155, 47.270111, 15.041932 , 55.099159]
    bbox2 = [-118.6, 14.39, -86.49, 32.72]
    assert similar.calculatedScore(bbox1, bbox2) == 0.6488100389180073

# Germany - Invalid input
def test_germany_invalid_input():
    bbox1 = [5.8663155, 47.270111, 15.041932 , 55.099159]
    bbox2 = ["abc"]
    assert similar.calculatedScore(bbox1, bbox2) == 1

# Germany - Germany
def test_germany_germany():
    bbox1 = [5.8663155, 47.270111, 15.041932 , 55.099159]
    bbox2 = [5.8663155, 47.270111, 15.041932 , 55.099159]
    assert similar.calculatedScore(bbox1, bbox2) == 0

# Invalid input - Invalid input
def test_invalid_invalid():
    bbox1 = ["cde"]
    bbox2 = ["abc"]
    assert similar.calculatedScore(bbox1, bbox2) == 1

"""
These tests check if the similarity score is multiplied with 5/4
if the datatypes are not equal
"""
# equal
def test_raster_raster():
    input1 = "raster.tif"
    input2 = "raster.csv"
    assert similar.whatDataType(input1, input2, 0.6) == 0.6

# equal
def test_vector_vector():
    input1 = "vector.geojson"
    input2 = "vector.shp"
    assert similar.whatDataType(input1, input2, 0.6) == 0.6

# not equal
def test_vector_raster():
    input1 = "test.csv"
    input2 = "test.shp"
    assert similar.whatDataType(input1, input2, 0.6) == 0.75

# not equal
def test_raster_vector():
    input1 = "test.tif"
    input2 = "test.gml"
    assert similar.whatDataType(input1, input2, 0.6) == 0.75

# sim score above 1
def test_overload():
    input1 = "test.nc"
    input2 = "test.tif"
    assert similar.whatDataType(input1, input2, 0.9) == 1

# if 0
def test_zero():
    input1 = "hallo.csv"
    input2 = "hallo.geojson"
    assert similar.whatDataType(input1, input2, 0) == 0

def test_extension_raster():
    filepath = "hallo.csv"
    assert similar.extension(filepath) == "raster"

def test_extension_vector():
    filepath = "test.shp"
    assert similar.extension(filepath) == "vector"
