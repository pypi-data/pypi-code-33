import click, json, sqlite3, csv, pygeoj, extractTool as de
from osgeo import gdal, ogr, osr
import pandas as pd
import numpy as np
import xarray as xr
import os
import sqlite3
from pyproj import Proj, transform
from scipy.spatial import ConvexHull

#Boolean variable that shows if the crs of the bbox is in wgs84
wgs_84=False
myCRS=""
"""
Function for extracting the bounding box of a geopackage file

:param filepath: path to the file
:param detail: specifies the level of detail of the geospatial extent (bbox or convex hull)
:param folder: specifies if the user gets the metadata for the whole folder (whole) or for each file (single)
:param time: boolean variable, if it is true the user gets the temporal extent instead of the spatial extent
:returns: spatial extent as a bbox in the format [minlon, minlat, maxlon, maxlat]
"""
def getGeopackagebbx(filepath, detail , time):
    """returns the bounding Box Geopackage
    @param path Path to the file
    @see https://docs.python.org/2/library/sqlite3.html"""
    
    
    if detail =='bbox':
        bbox_val=geopackage_bbox(filepath )

    else:
        bbox_val=[None]
    if detail == 'convexHull':
        convHull_val=geopackage_convHull(filepath )
        print(convHull_val)
    else:
        convHull_val=[None]
    if (time):
        time_val=geopackage_time(filepath )

    else:
        time_val=[None]


    ret_value=[bbox_val, convHull_val, time_val]
    return ret_value

def geopackage_time(filepath ):
    print("There is no time-value for GeoPackage files.")
    timeval=[None]
    return timeval

def geopackage_convHull(filepath ):
    conn = sqlite3.connect(filepath)
    c = conn.cursor()
    c.execute("""SELECT min_x,min_y, max_x, max_y, srs_id
                    FROM gpkg_contents""")
    
    points = c.fetchall()
    pointlist=[]
    print(points)
    for z in points:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        pointlist.append(de.transformToWGS84(z[0], z[1], myCRS))
        pointlist.append(de.transformToWGS84(z[2], z[3], myCRS))
    hull=ConvexHull(pointlist)
    hull_points=hull.vertices
    convHull=[]
    for y in hull_points:
        point=[pointlist[y][0], pointlist[y][1]]
        convHull.append(point)

    return convHull

def geopackage_bbox(filepath ):
    conn = sqlite3.connect(filepath)
    c = conn.cursor()
    # @see: https://www.geopackage.org/spec121/index.html#_contents_2
    c.execute("""SELECT min(min_y), min(min_x), max(max_y), max(max_x), srs_id
                    FROM gpkg_contents""")
    row = c.fetchall()
    try:
        lat1=row[0][0]
        lng1=row[0][1]
        lat2=row[0][2]
        lng2=row[0][3]
        myCRS=row[0][4]
        if not(lat1 and lat2):
            print("no coordinates")
    except (not(lat1 and lat2)):
        raise Exception ("There are no coordinate values in this file.")
        # Especially the KML data files have this id, which is wgs84
        # No need to transform
    if ((myCRS=="CRS84" or myCRS == 4326) and (lat1 and lng1)):
        wgs_84=True
        bbox=[lat1,lng1,lat2,lng2]
    elif(myCRS):
        wgs_84=True
        lat1t,lng1t = de.transformToWGS84(lat1,lng1,myCRS)
        lat2t,lng2t = de.transformToWGS84(lat2,lng2,myCRS)
        bbox=[lat1t,lng1t,lat2t,lng2t]
    else:
        print("There is no crs provided.")
        bbox=[lat1,lng1,lat2,lng2]

    if wgs_84==True:
        return bbox
    else:
        print("Missing CRS -----> Boundingbox will not be saved in zenodo.")
        return [None]

if __name__ == '__main__':
    getGeopackagebbx()
