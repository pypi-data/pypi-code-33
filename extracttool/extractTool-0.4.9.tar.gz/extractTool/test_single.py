import click        # used to print something
import os           # used to get the location of the testdata
import extractTool  # used for the the transformation and prints  

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

# Tests to check single files

###############################
# --detail=bbox --folder=single
###############################

def test_shapefile():
    filepath=__location__+'/testdata/Abgrabungen_Kreis_Kleve_shapefile/Abgrabungen_Kreis_Kleve_Shape.shp'
    assert extractTool.getMetadata(filepath, 'bbox' , False) == [[None], [None], [None]]

def test_csv():  
    filepath= __location__+'/testdata/cities_NL.csv'
    assert extractTool.getMetadata(filepath, 'bbox' , False) == [[4.3175, 51.434444000000006, 6.574722, 53.217222], [None], [None]]

def test_geopackage():
    filepath = __location__+'/testdata/Queensland_Children_geopackage/census2016_cca_qld_short.gpkg'    
    assert extractTool.getMetadata(filepath, 'bbox' , False) == [[96.8169, -43.7405, 167.998, -9.14218], [None], [None]]

def test_geojson():
    filepath=__location__+'/testdata/Abgrabungen_Kreis_Kleve.geojson'
    assert extractTool.getMetadata(filepath, 'bbox' , False) == [[6.04705316429154, 51.3721631194526, 6.4894453535296, 51.8440745554806], [None], [None]]

def test_geotiff():
    filepath=__location__+'/testdata/MittlWindgeschw-100m_GeoTIFF/wf_100m_klas.tif'
    assert extractTool.getMetadata(filepath, 'bbox' , False) == [[5.9153007564753155, 50.31025197410836, 9.468398712484145, 52.5307755328733], [None], [None]]

def test_gml_1():    
    filepath=__location__+'/testdata/clc_1000_PT.gml'
    assert extractTool.getMetadata(filepath, 'bbox' , False) == [[-17.54207241592243, 32.396692819320194, -6.95938792923511, 39.30113527461412], [None], [None]]

def test_gml_2():    
    filepath=__location__+"/testdata/mypolygon_px6.gml"
    assert extractTool.getMetadata(filepath, 'bbox' , False) == [[79.39064024773653, 11.627857397680971, 79.44763182487713, 11.697121798928404], [None], [None]]

def test_netcdf():    
    filepath= __location__+'/testdata/ECMWF_ERA-40_subset1.nc'
    assert extractTool.getMetadata(filepath, 'bbox' , False) == [[0.0,-90.0,  357.5, 90.0], [None], [None]]

#####################################
# --detail=convexHull --folder=single
# ################################### 

def test_convex_hull_shapefile():
    filepath=__location__+'/testdata/Abgrabungen_Kreis_Kleve_shapefile/Abgrabungen_Kreis_Kleve_Shape.shp'
    assert extractTool.getMetadata(filepath, 'convexHull' , False) == [[None], [None], [None]] 

def test_convex_hull_csv():  
    filepath=  __location__+'/testdata/cities_NL.csv'
    assert extractTool.getMetadata(filepath, 'convexHull' , False) == [[None], [[6.574722, 53.217222], [5.7925, 53.197222], [4.746389, 52.634443999999995], [4.3175, 52.084167], [4.4791669999999995, 51.930833], [5.484167, 51.434444], [5.9225, 51.999167]], [None]]

def test_convex_hull_geopackage():
    filepath = __location__+'/testdata/Queensland_Children_geopackage/census2016_cca_qld_short.gpkg'    
    assert extractTool.getMetadata(filepath, 'convexHull' , False) == [[None], [[137.99905382800011, -25.996866969999928], [140.99926498800005, -28.999101008999958], [151.34008239700006, -29.17737311299993], [151.34166839400007, -29.17739109599995], [151.393417547, -29.177894683999966], [151.3937835690001,-29.17789266699998], [151.3941365600001, -29.177839664999965], [151.3944875080001, -29.177694680999934], [152.00644910000005, -28.909157782999955], [152.00970300100005, -28.907662760999983], [153.53459401600003, -28.177638995999928], [153.55217124800004, -28.164408480999953], [153.54670756200005, -27.434827088999953], [153.3603268820001, -25.006193005999933], [153.35174810500007, -24.96573702099994], [153.2663279940001, -24.699736971999982], [153.2661289230001, -24.699200046999977], [143.87746788800007, -9.142926021999926], [143.87690808800005, -9.142306013999928], [143.87583816300003, -9.142175976999965], [142.15182012200012, -9.222157988999982], [142.15091003100008, -9.222278034999931], [142.14579010300008, -9.223198021999963], [141.57303297900012, -9.51290099199997], [141.57246314100007, -9.51347097699994], [141.5694031270001, -9.518450047999977], [137.9945999890001, -16.538260007999952], [137.99432499800002, -17.452575], [137.99687901200002, -25.13799899399993]], [None]]

def test_convex_hull_geojson():
    filepath=__location__+'/testdata/muenster_ring_zeit.geojson'
    assert extractTool.getMetadata(filepath, 'convexHull' , False) == [[None], [[7.6016807556152335, 51.96537036973145], [7.602796554565429, 51.953258408047034], [7.608118057250977, 51.94881477206191], [7.643308639526367, 51.953258408047034], [7.647256851196289, 51.95807185013927], [7.6471710205078125,51.96330786509095], [7.645540237426757, 51.96780294552556], [7.645368576049805, 51.96817310852836], [7.636871337890624, 51.97240332571046], [7.62125015258789, 51.974624029877454], [7.606401443481445, 51.97361943924433]], [None]]

def test_convex_hull_geotiff():
    filepath=__location__+'/testdata/MittlWindgeschw-100m_GeoTIFF/wf_100m_klas.tif'
    assert extractTool.getMetadata(filepath, 'convexHull' , False) == [[None], [None], [None]]

def test_convex_hull_gml():    
    filepath=__location__+'/testdata/mypolygon_px6.gml'
    assert extractTool.getMetadata(filepath, 'convexHull' , False) == [[None], [[79.39064024773653, 11.677958136567844], [79.39613341179829, 11.635255390466018], [79.42256926384478, 11.627857397680971], [79.44694517936921, 11.65307701972681], [79.44763182487713, 11.684009962648828], [79.40574644890594, 11.697121798928404]], [None]]

def test_convex_hull_netcdf():    
    filepath= __location__+'/testdata/ECMWF_ERA-40_subset1.nc'
    assert extractTool.getMetadata(filepath, 'convexHull' , False) == [[None], [None], [None]]
