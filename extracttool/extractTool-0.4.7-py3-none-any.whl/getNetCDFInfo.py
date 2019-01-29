
import click, json, sqlite3, csv, pygeoj, extractTool
from osgeo import gdal, ogr, osr
import pandas as pd
import numpy as np
import xarray as xr
import os
import dateparser   # used to parse the dates

"""
Function for extracting the bounding box of a NetCDF file

:param filepath: path to the file
:param detail: specifies the level of detail of the geospatial extent (bbox or convex hull)
:param folder: specifies if the user gets the metadata for the whole folder (whole) or for each file (single)
:param time: boolean variable, if it is true the user gets the temporal extent instead of the spatial extent
:returns: spatial extent as a bbox in the format [minlon, minlat, maxlon, maxlat]
"""
def getNetCDFbbx(filepath, detail, folder, time):
    #validation if file is netcdf
    if detail =='bbox':
        bbox_val=netcdf_bbox(filepath, folder)
    else:
        bbox_val=[None]

    if detail == 'convexHull':
        convHull_val=netcdf_convHull(filepath, folder)
    else:
        convHull_val=[None]

    # if time is selected (TRUE), the temporal extent is calculated
    if (time):
        time_val=netcdf_time(filepath, folder)
    else:
        time_val=[None]
    
    # if folder=='single':
    ret_value=[bbox_val, convHull_val, time_val]
    # print(ret_value)
    return ret_value
    #print("fertig")

"""
Function for extracting the time of a NetCDF file

:param filepath: path to the file
:param time: boolean variable, if it is true the user gets the temporal extent instead of the spatial extent
:returns: temporal extent
"""
def netcdf_time(filepath, folder):
    ds = xr.open_dataset(filepath)
    try:
        mytime = ds.coords["time"]
        # print(ds.values)
        starttime = min(mytime)
        endtime = max(mytime)
        # Zeitliche Ausdehnung
        anfang = str(starttime.values)
        ende = str(endtime.values)
        timemax_formatted=str(dateparser.parse(ende))
        timemin_formatted=str(dateparser.parse(anfang))
        #if folder=='single':
        # print("----------------------------------------------------------------")
        # click.echo("Filepath:")
        # click.echo(filepath)
        # print("the temporal extend of the NetCDF object is:")
        # print(timemin_formatted)
        # print(timemax_formatted)
        # print("----------------------------------------------------------------")
        return([timemin_formatted, timemax_formatted])
        #extractTool.ret_value.append([timemin_formatted, timemax_formatted])

        # if folder=='whole':
        #timeextend=[timemin_formatted, timemax_formatted]
        #extractTool.timeextendArray.append(timeextend)
        #print(timeextend[0])
        #print("timeextendArray:")
        #print(extractTool.timeextendArray)
        #return anfang, ende
        ds.close()
    except Exception as e:
        click.echo ("There is no time-value or invalid file")
        ds.close()
        return None

def netcdf_convHull(filepath, folder):
    ds = xr.open_dataset(filepath)
    # print("----------------------------------------------------------------")
    # click.echo("Filepath:")
    # click.echo(filepath)
    click.echo('Sorry there is no second level of detail for NetCDF files')
    # print("----------------------------------------------------------------")
    ds.close()
    return [None]
    #extractTool.ret_value.append([None])

def netcdf_bbox(filepath, folder):
    # print("bbox")
    ds = xr.open_dataset(filepath)
    try:
        lats = ds.coords["lat"]
        lons = ds.coords["lon"]

    except Exception as e:
        lats = ds.coords["latitude"]
        lons = ds.coords["longitude"]
    #print(ds.values)
    minlat=min(lats).values
    minlatFloat=float(minlat)
    minlon=min(lons).values
    minlonFloat=float(minlon)
    maxlat=max(lats).values
    maxlatFloat=float(maxlat)
    maxlon=max(lons).values
    maxlonFloat=float(maxlon)


    bbox = [minlatFloat,minlonFloat,maxlatFloat,maxlonFloat]
    #click.echo(bbox)

    #if folder=='single':
    extractTool.print_pretty_bbox(filepath,bbox, "NetCDF")
    ds.close()
    return bbox
    # if folder=='whole':
        #fuer Boundingbox des Ordners
    #    extractTool.bboxArray.append(bbox)
    #    click.echo(filepath)
    #    print(bbox)
    #    ds.close()
        #return bbox