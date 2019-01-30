import os   # used to get the location of the testdata
import extractTool # used to invoce the getMetadata function

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

######################################
# --detail=bbox --folder=single --time
######################################
def test_time_csv():  
    filepath=  __location__+'/testdata/cities_NL.csv'
    assert extractTool.getMetadata(filepath, 'bbox' , True) == [[4.3175, 51.434444000000006, 6.574722, 53.217222], [None], ['2018-09-30 00:00:00', '2018-09-30 00:00:00']]

def test_time_csv_none():  
    filepath=  __location__+'/testdata/Baumfaellungen_Duesseldorf.csv'
    assert extractTool.getMetadata(filepath, 'bbox' , True) == [[None],[None],[None]]

def test_time_shp():
    filepath=__location__+'/testdata/Abgrabungen_Kreis_Kleve_shapefile/Abgrabungen_Kreis_Kleve_Shape.shp'
    assert extractTool.getMetadata(filepath, 'bbox' , True) == [[None], [None], [None]]

def test_time_gpkg():
    filepath = __location__+'/testdata/Queensland_Children_geopackage/census2016_cca_qld_short.gpkg'    
    assert extractTool.getMetadata(filepath, 'bbox' , True) == [[96.8169, -43.7405, 167.998, -9.14218], [None], [None]]

def test_time_geojson():
    filepath=__location__+'/testdata/muenster_ring_zeit.geojson'
    assert extractTool.getMetadata(filepath, 'bbox' , True) == [[7.6016807556152335, 51.94881477206191, 7.647256851196289, 51.974624029877454], [None], ['2018-11-14 00:00:00', '2018-11-14 00:00:00']]

def test_time_gml():    
    filepath=__location__+'/testdata/clc_1000_PT.gml'
    assert extractTool.getMetadata(filepath, 'bbox' , True) == [[-17.54207241592243, 32.396692819320194, -6.95938792923511, 39.30113527461412], [None], [None]]

def test_time_geotiff():
    filepath=__location__+'/testdata/MittlWindgeschw-100m_GeoTIFF/wf_100m_klas.tif'
    assert extractTool.getMetadata(filepath, 'bbox' , True) == [[5.9153007564753155, 50.31025197410836, 9.468398712484145, 52.5307755328733], [None], [None]]

def test_time_netcdf():    
    filepath= __location__+'/testdata/ECMWF_ERA-40_subset1.nc'
    assert extractTool.getMetadata(filepath, 'bbox' , True) == [[0.0,-90.0, 357.5, 90.0], [None], ['2002-07-01 12:00:00', '2002-07-31 18:00:00']]
