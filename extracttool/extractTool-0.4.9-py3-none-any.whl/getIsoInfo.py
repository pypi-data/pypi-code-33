import click        # used to print something
import json         # used to parse kml and gml as json
import pygeoj       # used to parse kml and gml as json
import extractTool  # used for the prints
from osgeo import gdal  # used to print useful exceptions
import os            # used to get the location of the testdata   # used for folder handling
import ogr2ogr  # used to create help file
import tempfile # used to create help file
from scipy.spatial import ConvexHull  # used to calculate the convex hullimport geojson as gj
import xml.etree.ElementTree as ET
import dateparser   # used to parse the dates

#https://gis.stackexchange.com/questions/130963/write-geojson-into-a-geojson-file-with-python
# list which saves the points
point=list()
"""
Function for extracting coordinates of a feature.geometry.coordinates value and adds every point as a new point to the point list

:param geoj: feature.geometry.coordinates value of the geojson
:returns: point 
"""
def extract_coordinates(geoj):
    if (len(geoj)==2) and (type(geoj[0])==int or type(geoj[0])==float):
        new_point=[geoj[0], geoj[1]]
        point.append(geoj)
        return new_point
    else:
        for z in geoj:
            extract_coordinates(z)

"""
Auxiliary function to check if the file is a folder

:param filepath: path to the file
:returns: boolean value if the filepath contains a folder
"""
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
:param time: boolean variable, if it is true the user gets the temporal extent instead of the spatial extent
:returns: spatial extent as a bbox in the format [minlon, minlat, maxlon, maxlat]
"""
def getIsobbx(filepath, detail, time):
    gdal.UseExceptions()

    if (is_folder_check(filepath)):
        raise Exception ("This is a folder! ------> first opening it")
    
    ogr2ogr.main(["","-f", "GeoJSON", "out.json", filepath])

    """@see http://manpages.ubuntu.com/manpages/trusty/man1/ogr2ogr.1.html"""
    if detail =='bbox':
        bbox_val=iso_bbox(filepath)    
    else:
        bbox_val=[None]

    if detail =='convexHull':
        convex_hull_val=iso_convex_hull(filepath)
    else:
        convex_hull_val=[None]

    if (time):
        try: 
            time_val=iso_time(filepath)
        except Exception as e:
            print(e)        
    else:
        time_val=[None]
    
    ret_value=[bbox_val, convex_hull_val, time_val]
    os.remove("out.json")
    return ret_value

"""
Function for extracting the bounding box of an iso file

:param filepath: path to the file
:returns: spatial extent as a bbox in the format [minlon, minlat, maxlon, maxlat]
"""
def iso_bbox(filepath):
    defined_crs=True
    try:
        iso = pygeoj.load(filepath="out.json")
    except Exception as e:
        print(e)
    isobbx = (iso).bbox
    # Identification of CRS and transformation
    # In some test data the epsg id was stored in an unicode object like this one'urn:ogc:def:crs:EPSG::4258'
    try:
        iso_crs = (iso).crs
        my_crs= iso_crs["properties"]["name"]
        my_crs_str=my_crs.encode('ascii','ignore')
        # Extracting the epsg id
        my_split= my_crs_str.split(':')
        CRSID=my_split[len(my_split)-1]
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
        extractTool.print_pretty_bbox(filepath, mybbx, "ISO")
        return mybbx
        
    else:
        print("Missing CRS -----> Boundingbox will not be saved in zenodo.")
        return [None]

"""
Function for extracting the convex hull of an iso file

:param filepath: path to the file
:returns: convex hull of the iso file
"""
def iso_convex_hull(filepath):
    iso = pygeoj.load(filepath="out.json")
    #TO-DO feature.geometry.coordinates in variable speichern
    for feature in iso:
        try:
            f=feature.geometry.coordinates
            extract_coordinates(f)
        except Exception:
            click.echo("There is a feature without coordinates in the iso file")
       
    #calculation of the convex hull
    hull=ConvexHull(point)
    hull_points=hull.vertices
    convex_hull=[]
    for z in hull_points:
        hullcoord=[point[z][0], point[z][1]]
        convex_hull.append(hullcoord)
    return convex_hull

"""
Function for extracting the temporal extent of an iso file. 
We transform the gml file to a geojson file, then search for words like "date", "timestamp", "time" and collect them.

:param filepath: path to the file
:returns: time, meeting the ISO8601 standard, in the form [time, time]
"""
def iso_time(filepath):
    try:
        ogr2ogr.main(["","-f", "GeoJSON", "time.json", filepath])
    except Exception as e:
        click.echo(e)
    iso = open("time.json")
    geojson = json.load(iso)
    # :see: https://www.w3schools.com/python/python_file_remove.asp
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