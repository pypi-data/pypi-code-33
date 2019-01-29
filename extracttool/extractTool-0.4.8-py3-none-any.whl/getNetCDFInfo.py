
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
def getNetCDFbbx(filepath, detail , time):
    #validation if file is netcdf
    if detail =='bbox':
        bbox_val=netcdf_bbox(filepath )
    else:
        bbox_val=[None]

    if detail == 'convexHull':
        convHull_val=netcdf_convHull(filepath )
    else:
        convHull_val=[None]

    # if time is selected (TRUE), the temporal extent is calculated
    if (time):
        time_val=netcdf_time(filepath )
    else:
        time_val=[None]
    
    ret_value=[bbox_val, convHull_val, time_val]
    return ret_value
"""
Function for extracting the time of a NetCDF file

:param filepath: path to the file
:param time: boolean variable, if it is true the user gets the temporal extent instead of the spatial extent
:returns: temporal extent
"""
def netcdf_time(filepath ):
    ds = xr.open_dataset(filepath)
    try:
        mytime = ds.coords["time"]
        starttime = min(mytime)
        endtime = max(mytime)
        # Zeitliche Ausdehnung
        anfang = str(starttime.values)
        ende = str(endtime.values)
        timemax_formatted=str(dateparser.parse(ende))
        timemin_formatted=str(dateparser.parse(anfang))
        return([timemin_formatted, timemax_formatted])
        ds.close()
    except Exception as e:
        click.echo ("There is no time-value or invalid file")
        ds.close()
        return None

def netcdf_convHull(filepath ):
    ds = xr.open_dataset(filepath)
    click.echo('Sorry there is no second level of detail for NetCDF files')
    ds.close()
    return [None]

def netcdf_bbox(filepath ):
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
    extractTool.print_pretty_bbox(filepath,bbox, "NetCDF")
    ds.close()
    return bbox