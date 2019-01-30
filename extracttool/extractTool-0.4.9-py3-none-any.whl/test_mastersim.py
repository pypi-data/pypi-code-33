import click                  # used to print something
import mastersim #similar     # used to invoke the master function
import os                     # used to get the location of the testdata

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

#--detail
click.echo(__location__+'/testdata/')
"""
These tests check if the calucated similar score from two files is
equal to our hand-calculted score
"""

# Bei Tests die Tests 15/16/17 beeinflussen die anderen Tests und aders herum 
def test_mastersim_geojson_geotiff():
    filepath1 = __location__+'/testdata/Abgrabungen_Kreis_Kleve.geojson' 
    filepath2 = __location__+'/testdata/wf_100m_klas.tif'
    assert mastersim.master(filepath1, filepath2) == 0.02892620198410715

def test_mastersim_geojson_geopackage():
    filepath1 = __location__+'/testdata/Abgrabungen_Kreis_Kleve.geojson' 
    filepath2 = __location__+'/testdata/Queensland_Children_geopackage/census2016_cca_qld_short.gpkg'
    assert mastersim.master(filepath1, filepath2) == 1

def test_mastersim_geopackage_geotiff():
     filepath1 = __location__+'/testdata/Queensland_Children_geopackage/census2016_cca_qld_short.gpkg'
     filepath2 = __location__+'/testdata/wf_100m_klas.tif'
     assert mastersim.master(filepath1, filepath2) == 0.8222891646452265

#no crs info available in the shapefile
def test_mastersim_shapefile_equal():
     filepath1 = (__location__+'/testdata/Abgrabungen_Kreis_Kleve_shapefile/Abgrabungen_Kreis_Kleve_Shape.shp')
     filepath2 = (__location__+'/testdata/Abgrabungen_Kreis_Kleve_shapefile/Abgrabungen_Kreis_Kleve_Shape.shp')
     assert mastersim.master(filepath1, filepath2) == 1

def test_mastersim_geojson_equal():
    filepath1 = __location__+'/testdata/Abgrabungen_Kreis_Kleve.geojson' 
    filepath2 = __location__+'/testdata/Abgrabungen_Kreis_Kleve.geojson' 
    assert mastersim.master(filepath1, filepath2) == 0

def test_mastersim_geotiff_equal():
    filepath1 = __location__+'/testdata/wf_100m_klas.tif'
    filepath2 = __location__+'/testdata/wf_100m_klas.tif'
    assert mastersim.master(filepath1, filepath2) == 0

# No CRS info available
def test_mastersim_csv_equal():
    filepath1 = __location__+'/testdata/Behindertenparkplaetze_Duesseldorf.csv'
    filepath2 = __location__+'/testdata/Behindertenparkplaetze_Duesseldorf.csv'
    assert mastersim.master(filepath1, filepath2) == 1

def test_mastersim_netcdf_equal():
    filepath1 =__location__+'/testdata/ECMWF_ERA-40_subset1.nc'
    filepath2 = __location__+'/testdata/ECMWF_ERA-40_subset1.nc'
    assert mastersim.master(filepath1, filepath2) == 0


def test_mastersim_geopackage_equal():
    filepath1 = __location__+'/testdata/Queensland_Children_geopackage/census2016_cca_qld_short.gpkg'
    filepath2 = __location__+'/testdata/Queensland_Children_geopackage/census2016_cca_qld_short.gpkg'
    assert mastersim.master(filepath1, filepath2) == 0

def test_mastersim_gml_equal():
    filepath1 = __location__+'/testdata/3D_LoD1_33390_5664.gml'
    filepath2 = __location__+'/testdata/3D_LoD1_33390_5664.gml'
    assert mastersim.master(filepath1, filepath2) == 0

def test_mastersim_gml_geopackage():
    filepath1 = __location__+'/testdata/3D_LoD1_33390_5664.gml'
    filepath2 = __location__+'/testdata/Queensland_Children_geopackage/census2016_cca_qld_short.gpkg'
    assert mastersim.master(filepath1, filepath2) == 1

def test_mastersim_netcdf_geopackage():
    filepath1 = __location__+'/testdata/ECMWF_ERA-40_subset1.nc'
    filepath2 = __location__+'/testdata/Queensland_Children_geopackage/census2016_cca_qld_short.gpkg'
    assert mastersim.master(filepath1, filepath2) == 0.6570352358501073

# no crs info available in the shapefile
def test_mastersim_geojson_shapefile():
    filepath1 = __location__+'/testdata/Abgrabungen_Kreis_Kleve.geojson' 
    filepath2 = __location__+'/testdata/Abgrabungen_Kreis_Kleve.shp'
    assert mastersim.master(filepath1, filepath2) == 1

# no crs info available in the csv
def test_mastersim_geojson_csv():
    filepath1 = __location__+'/testdata/Abgrabungen_Kreis_Kleve.geojson' 
    filepath2 = __location__+'/testdata/Baumfaellungen_Duesseldorf.csv'
    assert mastersim.master(filepath1, filepath2) == 1

# no crs info available in the csv
def test_mastersim_csv_shapefile():
    filepath1 = __location__+'/testdata/Baumfaellungen_Duesseldorf.csv'
    filepath2 = __location__+'/testdata/Abgrabungen_Kreis_Kleve.shp'
    assert mastersim.master(filepath1, filepath2) == 1

# no crs info available in the shapefile
def test_mastersim_geotiff_shapefile():
    filepath1 = __location__+'/testdata/wf_100m_klas.tif'
    filepath2 = __location__+'/testdata/Abgrabungen_Kreis_Kleve.shp'
    assert mastersim.master(filepath1, filepath2) == 1

# no crs info available in the shapefile
def test_mastersim_gml_shapefile():
    filepath1 = __location__+'/testdata/3D_LoD1_33390_5664.gml'
    filepath2 = __location__+'/testdata/Abgrabungen_Kreis_Kleve.shp'
    assert mastersim.master(filepath1, filepath2) == 1