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
def getGeopackagebbx(filepath, detail, folder, time):
    """returns the bounding Box Geopackage
    @param path Path to the file
    @see https://docs.python.org/2/library/sqlite3.html"""
    
    
    if detail =='bbox':
        bbox_val=geopackage_bbox(filepath, folder)

    else:
        bbox_val=[None]
    if detail == 'convexHull':
        convHull_val=geopackage_convHull(filepath, folder)
        print("###############################################")
        print(convHull_val)
        print("###############################################")
    else:
        convHull_val=[None]
    if (time):
        time_val=geopackage_time(filepath, folder)

    else:
        time_val=[None]


    ret_value=[bbox_val, convHull_val, time_val]
    # print(ret_value)
    return ret_value

def geopackage_time(filepath, folder):
    out="There is no time-value for GeoPackage files."
    # print(out)
    timeval=[None]
    return timeval

def geopackage_convHull(filepath, folder):
    conn = sqlite3.connect(filepath)
    c = conn.cursor()
    c.execute("""SELECT min_x,min_y, max_x, max_y, srs_id
                    FROM gpkg_contents""")
    
    points = c.fetchall()
    pointlist=[]
    print("==================================")
    print(points)
    print("==================================")
    for z in points:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        pointlist.append(de.transformToWGS84(z[0], z[1], myCRS))
        pointlist.append(de.transformToWGS84(z[2], z[3], myCRS))
    hull=ConvexHull(pointlist)
    print("11111111111111111111111========")
    print(hull)
    print("11111111111111111111111==========")
    hull_points=hull.vertices
    convHull=[]
    for y in hull_points:
        point=[pointlist[y][0], pointlist[y][1]]
        convHull.append(point)
  
    # print("----------------------------------------------------------------")
    # click.echo("Filepath:")
    # click.echo(filepath)
    # click.echo("Convex hull of the GeoPackage object:")
    # print(convHull)
    # print("----------------------------------------------------------------")
    print(convHull)
    return convHull
    # if folder=='whole':
    #     print("----------------------------------------------------------------")
    #     de.bboxArray=de.bboxArray+convHull
    #     click.echo("convex hull whole")
    #     click.echo(convHull)
        

def geopackage_bbox(filepath, folder):
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
        # print("second if")
        wgs_84=True
        # print("vor")
        lat1t,lng1t = de.transformToWGS84(lat1,lng1,myCRS)
        # print("transformation success")
        lat2t,lng2t = de.transformToWGS84(lat2,lng2,myCRS)
        bbox=[lat1t,lng1t,lat2t,lng2t]
    else:
        print("There is no crs provided.")
        bbox=[lat1,lng1,lat2,lng2]


    #if folder=='single':
    if wgs_84==True:
        # print("----------------------------------------------------------------")
        # click.echo("Filepath:")
        # click.echo(filepath)
        # click.echo("Boundingbox of the GeoPackage object:")
        # print(bbox)
        # print("----------------------------------------------------------------")
        return bbox
    else:
        # print("----------------------------------------------------------------")
        # click.echo("Filepath:")
        # click.echo(filepath)
        # click.echo("Boundingbox of the GeoPackage object:")
        # print(bbox)
        print("Missing CRS -----> Boundingbox will not be saved in zenodo.")
        #print("----------------------------------------------------------------")
        return [None]
    # if folder=='whole':
    #     if wgs_84==True:
    #         de.bboxArray.append(bbox)
    #         print("----------------------------------------------------------------")
    #         click.echo("Filepath:")
    #         click.echo(filepath)
    #         click.echo("Boundingbox of the GeoPackage:")
    #         click.echo(bbox)
    #         print("----------------------------------------------------------------")
    #     else:
    #         print("----------------------------------------------------------------")
    #         click.echo("Filepath:")
    #         click.echo(filepath)
    #         click.echo("Boundingbox of the GeoPackage:")
    #         click.echo(bbox)
    #         click.echo("because of a missing crs this GeoPackage is not part of the folder calculation.")
    #         print("----------------------------------------------------------------")


if __name__ == '__main__':
    getGeopackagebbx()
