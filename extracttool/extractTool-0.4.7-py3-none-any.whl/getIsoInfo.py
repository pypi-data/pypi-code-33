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
def getIsobbx(filepath, detail, folder, time):
    
    gdal.UseExceptions()
    # click.echo("iso")

    if (is_folder_check(filepath)):
        raise Exception ("This is a folder! ------> first opening it")
    
    ogr2ogr.main(["","-f", "GeoJSON", "out.json", filepath])

    """@see http://manpages.ubuntu.com/manpages/trusty/man1/ogr2ogr.1.html"""
    if detail =='bbox':
        bbox_val=iso_bbox(filepath, folder)
    
    else:
        bbox_val=[None]
    #os.remove("out.json")

    if detail =='convexHull':
        print("//////////////////////////////////////////")
        convHull_val=iso_convHull(filepath, folder)
        
    else:
        convHull_val=[None]

    # We transform the gml file to a geojson file, then search for
    # words like "date", "timestamp", "time" and collect them
    if (time):
        try: 
            time_val=iso_time(filepath, folder)
        except Exception as e:
            print(e)
        
    else:
        time_val=[None]
    
    #if folder=='single':
    ret_value=[bbox_val, convHull_val, time_val]
    print("-----------------------------------------------")
    print(convHull_val)
    print("-----------------------------------------------")
    print(ret_value)
    print("-----------------------------------------------")
    # print(ret_value)
    os.remove("out.json")
    return ret_value
    #return time

def iso_bbox(filepath, folder):
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
        #if folder=='single':
        # print("----------------------------------------------------------------")
        # click.echo("filepath:")
        # click.echo(filepath)
        # click.echo("Boundingbox of the ISO object:")
        # click.echo(mybbx)
        # print("----------------------------------------------------------------")
        return mybbx
        #extractTool.ret_value.append(mybbx)

        # if folder=='whole':
        #     print("----------------------------------------------------------------")
        #     click.echo("filepath:")
        #     click.echo(filepath)
        #     click.echo("Boundingbox of the ISO object:")
        #     click.echo(mybbx)
        #     print("----------------------------------------------------------------")
        #     extractTool.bboxArray.append(mybbx)
    else:
        #if folder=='single':
        # print("----------------------------------------------------------------")
        # click.echo("filepath:")
        # click.echo(filepath)
        # click.echo("Boundingbox of the ISO object:")
        # click.echo(mybbx)
        print("Missing CRS -----> Boundingbox will not be saved in zenodo.")
        # print("----------------------------------------------------------------")
        return [None]
        #extractTool.ret_value.append([None])
        
        # if folder=='whole':
        #     print("----------------------------------------------------------------")
        #     click.echo("Filepath:")
        #     click.echo(filepath)
        #     click.echo("Boundingbox of the ISO object:")
        #     click.echo(mybbx)
        #     click.echo("because of a missing crs this ISO object is not part of the folder calculation.")
        #     print("----------------------------------------------------------------")


def iso_convHull(filepath, folder):
    # print("conv iso")
    #ogr2ogr.main(["","-f", "GeoJSON", "out.json", filepath])
    iso = pygeoj.load(filepath="out.json")
    #TO-DO feature.geometry.coordinates in variable speichern
    #points = 0
    for feature in iso:
        try:
            f=feature.geometry.coordinates
            extract_coordinates(f)
        except Exception:
            #TODO
            #hier besser raise exception?!
            print("There is a feature without coordinates in the iso file")
        # point.append(feature.geometry.coordinates)
        #print(point)
    #print(point)
    #calculation of the convex hull
    hull=ConvexHull(point)
    hull_points=hull.vertices
    print("555555555555555555555555555555555555555555")
    print(hull_points)
    print("555555555555555555555555555555555555555555")
    convHull=[]
    # print("afterhull")
    for z in hull_points:
        hullcoord=[point[z][0], point[z][1]]
        convHull.append(hullcoord)

    print(convHull)
        # print("in hull_points_loop")
    #if folder=='single':
    # print("----------------------------------------------------------------")
    # click.echo("Filepath:")
    # click.echo(filepath)
    # click.echo("Convex hull of the ISO object:")
    # click.echo(convHull)
    # print("----------------------------------------------------------------")
    return convHull
    #extractTool.ret_value.append([convHull])
    # if folder=='whole':
    #     print("----------------------------------------------------------------")
    #     extractTool.bboxArray=extractTool.bboxArray+convHull
    #     #extractTool.bboxArray.append(convHull)
    #     click.echo("convex hull whole")
    #     click.echo(convHull)
    #     print("bboxArray")
    #     print(extractTool.bboxArray)
    #     print("----------------------------------------------------------------")
    #os.remove("out.json")
    #iso.close()
    #return point



def iso_time(filepath, folder):
    print("time")
    try:
        ogr2ogr.main(["","-f", "GeoJSON", "time.json", filepath])
    except Exception as a:
        print (a)

    iso = open("time.json")

    geojson = json.load(iso)
    # @see https://www.w3schools.com/python/python_file_remove.asp
    os.remove("time.json")
    if geojson["type"] == "FeatureCollection":
        #print(geojson["features"])
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
                                            #extractTool.ret_value.append([None])
                                            #print(extractTool.ret_value)
                                            #return(extractTool.ret_value)
                                            click.echo("There is no time-value ISO")
                                            #click.echo("there is no time-value ISO")
                                            #print(time)
                                            return [None]   

        time_formatted=dateparser.parse(time)
        timeextend=[time_formatted, time_formatted]

        #extractTool.ret_value.append([timeextend])
        # print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        # print(timeextend)
        return timeextend
        #print("The time value of this ISO file is:")
        #print(time)
