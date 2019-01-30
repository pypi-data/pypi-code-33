import click        # used to print something
import os           # used to get the location of the testdata
import extractTool  # used to invoke the getMetadata function

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

# Tests to check folders

###############################
# --detail=bbox --folder=whole
###############################
def test_whole_mix_1():
    filepath=__location__+'/testdata/mischung_bbox1'
    assert extractTool.getMetadata(filepath, 'bbox' , False) == [[5.9153007564753155, -43.7405, 167.998, 52.5307755328733], [None], [None]]

def test_whole_mix_2():  
    filepath=__location__+"/testdata/mischung_bbox2"  
    assert extractTool.getMetadata(filepath, 'bbox' , False) == [[5.520648869321924, 49.87014441103477, 10.114607987362609, 52.88446415203189], [None], [None]]

def test_whole_geotiff():    
    filepath=__location__+'/testdata/geotifftest'
    assert extractTool.getMetadata(filepath, 'bbox' , False) == [[5.520648869321924, 49.87014441103477, 10.114607987362609, 52.88446415203189], [None], [None]]

def test_whole_geopackage():  
    filepath=__location__+"/testdata/geopackagetest"  
    assert extractTool.getMetadata(filepath, 'bbox' , False) == [[96.8169, -43.7405, 167.998, -9.14218], [None], [None]]

def test_whole_csv():
    filepath=__location__+"/testdata/csvordnertest"
    assert extractTool.getMetadata(filepath, 'bbox' , False) == [[4.3175, 47.988889, 9.731219, 53.217222], [None], [None]]

def test_whole_geojson():
    filepath=__location__+"/testdata/innergeoj"
    assert extractTool.getMetadata(filepath, 'bbox', False) == [[6.60864, 51.2380774, 6.71483, 51.31549], [None], [None]]


#####################################
# --detail=bbox --folder=whole --time
#####################################

def test_whole_time_geojson():
    filepath=__location__+"/testdata/timegeo/timegeo"
    assert extractTool.getMetadata(filepath, 'bbox' , True) == [[6.220493316650391, 50.52150360276628, 7.647256851196289, 51.974624029877454], [None], ['2018-11-14 00:00:00', '2018-11-14 00:00:00']]

def test_whole_time_mix():    
    filepath=__location__+"/testdata/time_mischung"
    assert extractTool.getMetadata(filepath, 'bbox', True) == [[0.0,-90.0, 357.5, 90.0], [None], ['2002-07-01 12:00:00', '2018-11-14 00:00:00']]

def test_whole_time_empty():    
    filepath=__location__+"/testdata/leer"
    assert extractTool.getMetadata(filepath, 'bbox', True) == None


#####################################
# --detail=convexHull --folder=whole 
#####################################

def test_whole_hull_mix_1():
    filepath=__location__+'/testdata/mischung_bbox1'
    assert extractTool.getMetadata(filepath, 'convexHull', False) == [[None], [None], [None]]

def test_whole_hull_mix_2():  
    filepath=__location__+"/testdata/mischung_bbox2"  
    assert extractTool.getMetadata(filepath, 'convexHull', False) == [[None], [None], [None]]

def test_whole_hull_geotiff():    
    filepath=__location__+'/testdata/geotifftest'
    assert extractTool.getMetadata(filepath, 'convexHull', False) == [[None], [None], [None]]

def test_whole_hull_geopackage():  
    filepath=__location__+"/testdata/geopackagetest"  
    assert extractTool.getMetadata(filepath, 'convexHull', False) == [[None], [None], [None]]

def test_whole_hull_csv():
    filepath=__location__+"/testdata/csvordnertest"
    assert extractTool.getMetadata(filepath, 'convexHull', False) == [[None], [None], [None]]

def test_whole_hull_geojson():
    filepath=__location__+"/testdata/innergeoj"
    assert extractTool.getMetadata(filepath, 'convexHull', False) == [[None], [None], [None]]

###########################################
# --detail=convexHull --folder=whole --time 
###########################################

def test_whole_hull_time_geojson():
    filepath=__location__+"/testdata/timegeo/timegeo"
    assert extractTool.getMetadata(filepath, 'convexHull', True) == [[None], [None], ['2018-11-14 00:00:00', '2018-11-14 00:00:00']]

def test_whole_hull_time_mix():    
    filepath=__location__+"/testdata/time_mischung"
    assert extractTool.getMetadata(filepath, 'convexHull', True) == [[None], [None], ['2002-07-01 12:00:00', '2018-11-14 00:00:00']]

def test_whole_hull_time_empty():    
    filepath=__location__+"/testdata/leer"
    assert extractTool.getMetadata(filepath, 'convexHull', True) == None

###########################################
# --detail=bbox folder in folder 
###########################################

def test_folder_folder():    
    filepath=__location__+"/testdata/folder"
    assert extractTool.getMetadata(filepath, 'bbox', False) == [[6.59663465544554, 51.2380774, 6.71483, 51.486636388722296], [None], [None]]
