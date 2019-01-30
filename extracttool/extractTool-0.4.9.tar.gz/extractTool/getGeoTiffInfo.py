import click        # used to print something 
from osgeo import gdal, osr     # used to open and parse the file
import extractTool  # used for the prints

"""
Function for extracting the spatial and temporal information of a GeoTIFF 

:param filepath: path to the file
:param detail: specifies the level of detail of the geospatial extent (bbox or convex hull)
:param time: boolean variable, if it is true the user gets the temporal extent instead of the spatial extent
:returns: spatial and temporal information in the format [[bounding box],[convex Hull],[temporal extent]]
"""
def getGeoTiffbbx(filepath, detail, time):
    gdal.UseExceptions()
    """@see https://stackoverflow.com/questions/2922532/obtain-latitude-and-longitude-from-a-geotiff-file"""

    if detail =='bbox':
        bbox_val=tiff_bbox(filepath)
    else:
        bbox_val=[None]

    # The second level of detail is not reasonable for geotiffs because they are rasterdata.
    if detail == 'convexHull':
        convex_hull_val=tiff_convex_hull(filepath)
    else:
        convex_hull_val=[None]

    if (time):
        time_val=tiff_time(filepath)
    else:
        time_val=[None]

    ret_value=[bbox_val, convex_hull_val, time_val]
    return ret_value

"""
Function for extracting the temporal extent of a GeoTIFF, but for now there is no time value for geopackage files. So it just returns None.

:param filepath: path to the file
:returns: None
"""
def tiff_time(filepath):
    click.echo('There is no time value for GeoTIFF files')
    return [None]

"""
Function for extracting the convex hull. 

:param filepath: path to the file
:returns: None, because GeoTIFFs are raster data and convex Hull of raster data equals the bounding box.
"""
def tiff_convex_hull(filepath):
    gdal.Open(filepath)
    click.echo('There is no convex hull for GeoTIFF files.')
    return [None]

"""
Function for extracting the bbox using gdal

:param filepath: path to the file
:returns: bounding box of the GeoTIFF in the format [minlon, minlat, maxlon, maxlat]
"""
def tiff_bbox(filepath):
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
        new_cs.ImportFromWkt(wgs84_wkt)

        # create a transform object to convert between coordinate systems
        transform = osr.CoordinateTransformation(old_cs,new_cs)
    except Exception:
        wgs_84=False

    # get the point to transform, pixel (0,0) in this case
    width = ds.RasterXSize
    height = ds.RasterYSize
    gt = ds.GetGeoTransform()

    lon_min = gt[0]
    lat_min = gt[3] + width*gt[4] + height*gt[5]
    lon_max = gt[0] + width*gt[1] + height*gt[2]
    lat_max = gt[3]

    # get the coordinates in lat long
    lat_lon_min = transform.TransformPoint(lon_min,lat_min)
    lat_lon_max = transform.TransformPoint(lon_max,lat_max)
    bbox = [lat_lon_min[0], lat_lon_min[1], lat_lon_max[0], lat_lon_max[1]]    
    extractTool.print_pretty_bbox(filepath, bbox, "GeoTIFF")

    if wgs_84==True:
        return bbox
    else:
        print("Missing CRS -----> Boundingbox will not be saved in zenodo.")
        return [None]
    
if __name__ == '__main__':
    getGeoTiffbbx()