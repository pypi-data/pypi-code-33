import click
import extractTool
from osgeo import gdal, ogr, osr

"""
Function for extracting a bounding box of a GeoTIFF file

:param filepath: path to the file
:param detail: specifies the level of detail of the geospatial extent (bbox or convex hull)
:param folder: specifies if the user gets the metadata for the whole folder (whole) or for each file (single)
:param time: boolean variable, if it is true the user gets the temporal extent instead of the spatial extent
:returns: spatial extent as a bbox in the format [minlon, minlat, maxlon, maxlat]
"""
def getGeoTiffbbx(filepath, detail , time):
    #Boolean variable that shows if the crs of the bbox is in wgs84
    
    gdal.UseExceptions()
    
    """@see https://stackoverflow.com/questions/2922532/obtain-latitude-and-longitude-from-a-geotiff-file"""

    if detail =='bbox':
        bbox_val=tiff_bbox(filepath )
    else:
        bbox_val=[None]

    """second level of detail is not reasonable for geotiffs because they are rasterdata."""
    if detail == 'convexHull':
        convHull_val=tiff_convexHull(filepath )
        
    else:
        convHull_val=[None]

    if (time):
        time_val=tiff_time(filepath )
    else:
        time_val=[None]

    ret_value=[bbox_val, convHull_val, time_val]
    return ret_value

def tiff_time(filepath ):
    click.echo('There is no time value for GeoTIFF files')
    timeval=[None]
    return timeval

def tiff_convexHull(filepath ):
    gdal.Open(filepath)
    click.echo('There is no convex hull for GeoTIFF files.')
    return [None]

def tiff_bbox(filepath ):
    """CRS Transformation"""
    wgs_84=True
    ds = gdal.Open(filepath)
    try:
        #get the existing coordinate system
        old_cs= osr.SpatialReference()
        old_cs.ImportFromWkt(ds.GetProjectionRef())

        # create the new coordinate system
        wgs84_wkt = """
        GEOGCS["WGS 84",
            DATUM["WGS_1984",
                SPHEROID["WGS 84",6378137,298.257223563,
                    AUTHORITY["EPSG","7030"]],
                AUTHORITY["EPSG","6326"]],
            PRIMEM["Greenwich",0,
                AUTHORITY["EPSG","8901"]],
            UNIT["degree",0.01745329251994328,
                AUTHORITY["EPSG","9122"]],
            AUTHORITY["EPSG","4326"]]"""
        new_cs = osr.SpatialReference()
        new_cs .ImportFromWkt(wgs84_wkt)

        # create a transform object to convert between coordinate systems
        transform = osr.CoordinateTransformation(old_cs,new_cs)
    except Exception:
        wgs_84=False

    #get the point to transform, pixel (0,0) in this case
    width = ds.RasterXSize
    height = ds.RasterYSize
    gt = ds.GetGeoTransform()

    minx = gt[0]
    miny = gt[3] + width*gt[4] + height*gt[5]
    maxx = gt[0] + width*gt[1] + height*gt[2]
    maxy = gt[3]
    #get the coordinates in lat long
    latlongmin = transform.TransformPoint(minx,miny)
    latlongmax = transform.TransformPoint(maxx,maxy)
    bbox = [latlongmin[0], latlongmin[1], latlongmax[0], latlongmax[1]]

    if wgs_84==True:
        return bbox
    else:
        print("Missing CRS -----> Boundingbox will not be saved in zenodo.")
        return [None]
    
if __name__ == '__main__':
    getGeoTiffbbx()