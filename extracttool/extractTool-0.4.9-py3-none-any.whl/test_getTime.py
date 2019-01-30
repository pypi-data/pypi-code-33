import os            # used to get the location of the testdata
import getTimeextent # used to invoke the get time functions of the specific datatypes

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

# Tests for our getTimeextend file. This file is just for testing.
# The single fuctions are included in our extractTool.py 

def test_timeShape():
    assert getTimeextent.getShapefiletime(__location__+'/testdata/Abgrabungen_Kreis_Kleve_shapefile/Abgrabungen_Kreis_Kleve_Shape.shp', 'time') == None

def test_timeCSV():    
    assert getTimeextent.getCSVtime(__location__+'/testdata/Baumfaellungen_Duesseldorf.csv', 'time' ) == None

def test_timeGeoPackage():    
    assert getTimeextent.getGeopackagetime(__location__+'/testdata/Geopackage_Queensland_geopackage/census2016_cca_qld_short.gpkg', 'time') == None

def test_timeGeoJson():    
    assert getTimeextent.getGeoJsontime(__location__+'/testdata/muenster_ring_zeit.geojson', 'time') == "2018-11-14"

def test_timeGeoTiff():    
    assert getTimeextent.getGeoTifftime(__location__+'/testdata/MittlWindgeschw-100m_GeoTIFF/wf_100m_klas.tif', 'time') == None

def test_timeIso():    
     assert getTimeextent.getIsoTime(__location__+'/testdata/clc_1000_PT.gml', 'time') == "2012-09-09"

def test_timeNetCDF():    
    assert getTimeextent.getNetCDFtime(__location__+'/testdata/ECMWF_ERA-40_subset1.nc', 'time') == ['2002-07-01T12:00:00.000000000', '2002-07-31T18:00:00.000000000']
