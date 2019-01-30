import click        # used to print something
import extractTool  # used for the the transformation and prints
import sqlite3      # used to access the geopackage database, :see:  https://docs.python.org/2/library/sqlite3.html
from scipy.spatial import ConvexHull  # used to calculate the convex hull

"""
Function for extracting the bounding box of a geopackage file

:param filepath: path to the file
:param detail: specifies the level of detail of the geospatial extent (bbox or convex hull)
:param time: boolean variable, if it is true the user gets the temporal extent instead of the spatial extent
:returns: spatial and temporal information in the format [[bounding box],[convex Hull],[temporal extent]]
"""
def getGeopackagebbx(filepath, detail, time):
    if detail =='bbox':
        bbox_val=geopackage_bbox(filepath)
    else:
        bbox_val=[None]

    if detail == 'convexHull':
        convex_hull_val=geopackage_convex_hull(filepath)
    else:
        convex_hull_val=[None]

    if (time):
        time_val=geopackage_time(filepath)
    else:
        time_val=[None]

    ret_value=[bbox_val, convex_hull_val, time_val]
    return ret_value

"""
Function that should extract the temporal extent of a geopackage file, but for now there is no time value for geopackage files. So it just returns None.

:param filepath: path to the file
:returns: None
"""
def geopackage_time(filepath):
    click.echo("There is no time-value for GeoPackage files.")
    timeval=[None]
    return timeval

"""
Function for extracting the convex hull

:param filepath: path to the file
:returns: convex hull of the geojson
"""
def geopackage_convex_hull(filepath):
    # accessing the database
    conn = sqlite3.connect(filepath)
    c = conn.cursor()
    # retrieving coordinate values and crs information
    c.execute("""SELECT min_x, min_y, max_x, max_y, srs_id FROM gpkg_contents""")
    points = c.fetchall()
    point_list=[]
    for z in points:
        point_list.append(extractTool.transformToWGS84(z[0], z[1], z[5]))
        point_list.append(extractTool.transformToWGS84(z[2], z[3], z[5]))
    hull=ConvexHull(point_list)
    hull_points=hull.vertices
    convex_hull=[]
    for y in hull_points:
        point=[point_list[y][0], point_list[y][1]]
        convex_hull.append(point)
    return convex_hull

"""
Function for extracting the bbox using sqlite3

:see: https://www.geopackage.org/spec121/index.html#_contents_2
:param filepath: path to the file
:returns: bounding box of the geopackage in the format [minlon, minlat, maxlon, maxlat]
"""
def geopackage_bbox(filepath):
    conn = sqlite3.connect(filepath)
    c = conn.cursor()
    c.execute("""SELECT min(min_x), min(min_y), max(max_x), max(max_y), srs_id FROM gpkg_contents""")
    row = c.fetchall()
    try:
        min_lon=row[0][0]
        min_lat=row[0][1]
        max_lon=row[0][2]
        max_lat=row[0][3]
        myCRS=row[0][4]
    except Exception:
        click.echo("There are no coordinate values in this file.")
        raise 
        
    if ((myCRS=="CRS84" or myCRS == 4326) and (min_lon and min_lat)):
        crs_info=True
        bbox=[min_lon,min_lat,max_lon,max_lat]
    elif(myCRS):
        crs_info=True
        min_lon_t,min_lat_t = extractTool.transformToWGS84(min_lon,min_lat,myCRS)
        max_lon_t,max_lat_t = extractTool.transformToWGS84(max_lon,max_lat,myCRS)
        bbox=[min_lon_t,min_lat_t,max_lon_t,max_lat_t]
    else:
        click.echo("There is no crs provided.")
        bbox=[min_lon,min_lat,max_lon,max_lat]

    if (crs_info):
        extractTool.print_pretty_bbox(filepath, bbox, "GeoJSON")
        return bbox
    else:
        click.echo("Missing CRS -----> Boundingbox will not be saved in zenodo.")
        return [None]

if __name__ == '__main__':
    getGeopackagebbx()
