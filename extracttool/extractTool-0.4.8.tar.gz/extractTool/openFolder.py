import click, json, sqlite3, csv, pygeoj
from osgeo import gdal, ogr, osr
import pandas as pd
import numpy as np
import xarray as xr
import os
import getShapefileInfo, getGeoTiffInfo, getCSVInfo, getIsoInfo, getGeoJsonInfo, getNetCDFInfo, getGeoPackageInfo, extractTool
from scipy.spatial import ConvexHull

"""
Function for extracting the spatial extent from a directory of files

:param filepath: path to the directory of the files
:param detail: specifies the level of detail of the geospatial extent (bbox or convex hull)
:param folder: specifies if the user gets the metadata for the whole folder (whole) or for each file (single)
:param time: boolean variable, if it is true the user gets the temporal extent instead of the spatial extent
:returns: spatial extent as a bbox in the format [minlon, minlat, maxlon, maxlat]
"""

def openFolder(filepath, detail , time):
    #Es kann sein, dass hier keine ordner extrahiert werden koennen, die in anderen
    #Ordnern liegen.
    folder_bboxArray=[]
    folder_convHullArray=[]
    folder_timeArray=[]
    folderpath= filepath
    docs=os.listdir(folderpath) 
    # docs now contains the files of the folder 
    # tries to extract the bbox of each file 
    for x in docs:  
        docPath= folderpath +"/"+ x
        try:
            b=getShapefileInfo.getShapefilebbx(docPath, detail , time)
        except Exception as e:
            try:
                b=getGeoJsonInfo.getGeoJsonbbx(docPath, detail , time)
            except Exception as e:
                try:
                    click.echo(e)
                    b=getNetCDFInfo.getNetCDFbbx(docPath, detail , time)
                except Exception as e:
                    try:
                        b=getCSVInfo.getCSVbbx(docPath, detail , time)
                    except ValueError as err:
                        # print(err.args)
                        continue
                    except TypeError as e:
                        try:
                            b=getGeoTiffInfo.getGeoTiffbbx(docPath, detail , time)
                        except Exception as e:
                            try:
                                b=getGeoPackageInfo.getGeopackagebbx(docPath, detail , time)
                                print("after geopackage")
                            except Exception as e:
                                try:
                                    b=getIsoInfo.getIsobbx(docPath, detail , time)
                                except Exception as e:
                                    try:
                                        b=openFolder(docPath, detail , time)
                                    except Exception as e:
                                        click.echo ("invalid file format in folder!")
                                        b=None
                               
        if (b[0]!=[None]):
            folder_bboxArray=folder_bboxArray+[b[0]]
        if (b[1]!= [None]):
            folder_convHullArray=folder_convHullArray+[b[1]]
        if (b[2]!=[None]):
            folder_timeArray=folder_timeArray+[b[2]]
    
    ret_value_folder=[]                            
    if detail=='bbox':
        bboxes=folder_bboxArray
        lat1List=[lat1 for lat1, lng1, lat2, lng2 in bboxes]
        for x in lat1List:
            try:
                if x<min1:
                    min1=x
            except NameError:
                min1 = x

        lng1List=[lng1 for lat1, lng1, lat2, lng2 in bboxes]
        for x in lng1List:
            try:
                if x<min2:
                    min2=x
            except NameError:
                min2 = x

        lat2List=[lat2 for lat1, lng1, lat2, lng2 in bboxes]
        for x in lat2List:
            try:
                if x>max1:
                    max1=x
            except NameError:
                max1=x

        lng2List=[lng2 for lat1, lng1, lat2, lng2 in bboxes]
        for x in lng2List:
            try:
                if x>max2:
                    max2=x
            except NameError:
                max2=x

        folderbbox=[min1, min2, max1, max2]
        ret_value_folder.append(folderbbox)
    else:
        ret_value_folder.append([None])
    if detail=='convexHull':
        click.echo("There is no convex hull for directories.")
        #gibts jetzt eh nicht mehr -> das kann irgendwie geloescht werden :)
        # points=folder_convHullArray
        # hull=ConvexHull(points)
        # hull_points=hull.vertices
        # convHull=[]
        # for y in hull_points:
        #     point=[points[y][0], points[y][1]]
        #     convHull.append(point)
        # # click.echo("convex hull of the folder:")    
        # click.echo(convHull)
        # #return convHull
        ret_value_folder.append([None])
    else:
        ret_value_folder.append([None])
    if (time):
        times=folder_timeArray
        mindate=[]
        maxdate=[]
        for z in times:
            mindate.append(z[0])
            maxdate.append(z[1])
        min_mindate=min(mindate)
        max_maxdate=max(maxdate)
        folder_timeextend=[min_mindate, max_maxdate]
        if (times):
            ret_value_folder.append(folder_timeextend)
        else:
            ret_value_folder.append([None])

    else:
        ret_value_folder.append([None])
    return ret_value_folder

        


if __name__ == '__main__':
    openFolder()