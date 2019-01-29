import click, json, sqlite3, csv, pygeoj, extractTool
from osgeo import gdal, ogr, osr
import pandas as pd
import numpy as np
import xarray as xr
import os
import ogr2ogr
#new for this module
import tempfile
from scipy.spatial import ConvexHull
import geojson as gj
import xml.etree.ElementTree as ET
import dateparser

#https://gis.stackexchange.com/questions/130963/write-geojson-into-a-geojson-file-with-python

point=list()
#in diese methode muss ein feature.geometry.coordinates wert eingefuegt werden.
def extract_coordinates(geoj):
    if (len(geoj)==2) and (type(geoj[0])==int or type(geoj[0])==float):
        new_point=[geoj[0], geoj[1]]
        point.append(geoj)
        return new_point
    else:
        for z in geoj:
            extract_coordinates(z)

#without this function getIsobbx would open a folder and extract metadata the wrong way.
def is_folder_check(filepath):
    is_folder=False
    try:
        os.listdir(filepath)
        is_folder=True
    except Exception:
        pass
    return is_folder

"""
Function for extracting the bounding box of an iso file

:param filepath: path to the file
:param detail: specifies the level of detail of the geospatial extent (bbox or convex hull)
:param folder: specifies if the user gets the metadata for the whole folder (whole) or for each file (single)
:param time: boolean variable, if it is true the user gets the temporal extent instead of the spatial extent
:returns: spatial extent as a bbox in the format [minlon, minlat, maxlon, maxlat]
"""
def getIsobbx(filepath, detail , time):
    gdal.UseExceptions()

    if (is_folder_check(filepath)):
        raise Exception ("This is a folder! ------> first opening it")
    
    ogr2ogr.main(["","-f", "GeoJSON", "out.json", filepath])

    """@see http://manpages.ubuntu.com/manpages/trusty/man1/ogr2ogr.1.html"""
    if detail =='bbox':
        bbox_val=iso_bbox(filepath )
    
    else:
        bbox_val=[None]

    if detail =='convexHull':
        convHull_val=iso_convHull(filepath )
        
    else:
        convHull_val=[None]

    # We transform the gml file to a geojson file, then search for
    # words like "date", "timestamp", "time" and collect them
    if (time):
        try: 
            time_val=iso_time(filepath )
        except Exception as e:
            print(e)
        
    else:
        time_val=[None]
    
    ret_value=[bbox_val, convHull_val, time_val]
    os.remove("out.json")
    return ret_value

def iso_bbox(filepath ):
    defined_crs=True
    try:
        iso = pygeoj.load(filepath="out.json")
    except Exception as e:
        print(e)
    isobbx = (iso).bbox
    # Identification of CRS and transformation
    # In some test data the epsg id was stored in an unicode object like this one'urn:ogc:def:crs:EPSG::4258'
    try:
        isocrs = (iso).crs
        mycrs= isocrs["properties"]["name"]
        mycrsString=mycrs.encode('ascii','ignore')
        # Extracting the epsg id
        mySplit= mycrsString.split(':')
        CRSID=mySplit[len(mySplit)-1]
        # Especially the KML data files have this id, which is wgs84
        # No need to transform
        if (CRSID=="CRS84" or CRSID == 4326):
            mybbx=[isobbx[0],isobbx[1],isobbx[2],isobbx[3]]
        else:
            lat1t,lng1t=extractTool.transformToWGS84(isobbx[0],isobbx[1],CRSID)
            lat2t,lng2t=extractTool.transformToWGS84(isobbx[2],isobbx[3],CRSID)
            mybbx=[lat1t,lng1t,lat2t,lng2t]
    except:
        print("While splitting the string an error occurred")
        defined_crs=False
    if defined_crs:
        return mybbx
        
    else:
        print("Missing CRS -----> Boundingbox will not be saved in zenodo.")
        return [None]

def iso_convHull(filepath ):
    iso = pygeoj.load(filepath="out.json")
    #TO-DO feature.geometry.coordinates in variable speichern
    for feature in iso:
        try:
            f=feature.geometry.coordinates
            extract_coordinates(f)
        except Exception:
            #TODO
            #hier besser raise exception?!
            print("There is a feature without coordinates in the iso file")
       
    #calculation of the convex hull
    hull=ConvexHull(point)
    hull_points=hull.vertices
    convHull=[]
    for z in hull_points:
        hullcoord=[point[z][0], point[z][1]]
        convHull.append(hullcoord)

    return convHull

def iso_time(filepath ):
    try:
        ogr2ogr.main(["","-f", "GeoJSON", "time.json", filepath])
    except Exception as a:
        print (a)

    iso = open("time.json")

    geojson = json.load(iso)
    # @see https://www.w3schools.com/python/python_file_remove.asp
    os.remove("time.json")
    if geojson["type"] == "FeatureCollection":
        first = geojson["features"]  
        time = []
        for i in range(0,5):            
            try:
                time = first[i]["Date"]
                return time
            except Exception as e:
                try:
                    time = time[i]["properties"]["creationDate"]
                    return time
                except Exception as e:
                    try:
                        time = first[i]["date"]
                        return time
                    except Exception as e:
                        try:
                            time = first[i]["time"]
                            return time
                        except Exception as e:
                            try:
                                time = first[i]["properties"]["date"]
                                return time
                            except Exception as e:
                                try:
                                    time = first[i]["properties"]["time"]
                                    return time
                                except Exception as e:
                                    try:
                                        time = first[i]["Start_Date"]
                                        return time
                                    except Exception as e:
                                        try:
                                            time = first[i]["timeStamp"]
                                            return time
                                        except Exception as e:
                                            #this exception is important for folder time extraction of cvs files...DONT DELETE IT!
                                            click.echo("There is no time-value ISO")
                                            return [None]   

        time_formatted=dateparser.parse(time)
        timeextend=[time_formatted, time_formatted]
        return timeextend