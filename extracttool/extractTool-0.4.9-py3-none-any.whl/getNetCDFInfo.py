import click        # used to print something , 
import json, sqlite3, csv, pygeoj, extractTool
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
:param time: boolean variable, if it is true the user gets the temporal extent instead of the spatial extent
:returns: spatial extent as a bbox in the format [minlon, minlat, maxlon, maxlat]
"""
def getNetCDFbbx(filepath, detail, time):
    #validation if file is netcdf
    if detail =='bbox':
        bbox_val=netcdf_bbox(filepath)
    else:
        bbox_val=[None]

    if detail == 'convexHull':
        convHull_val=netcdf_convHull(filepath)
    else:
        convHull_val=[None]

    # if time is selected (TRUE), the temporal extent is calculated
    if (time):
        time_val=netcdf_time(filepath)
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
def netcdf_time(filepath):
    ds = xr.open_dataset(filepath)
    try:
        mytime = ds.coords["time"]
        starttime = min(mytime)
        endtime = max(mytime)
        # Time extend
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

"""
Function for extracting the convex hull of a NetCDF file

:param filepath: path to the file
:returns: None, because netCDF are raster data and convex Hull of raster data equals the bounding box.
"""
def netcdf_convHull(filepath):
    ds = xr.open_dataset(filepath)
    ds.close()
    return [None]

"""
Function for extracting the bbox 

:param filepath: path to the file
:returns: bounding box of the netCDF in the format [minlon, minlat, maxlon, maxlat]
"""
def netcdf_bbox(filepath):
    ds = xr.open_dataset(filepath)
    try:
        lats = ds.coords["lat"]
        lons = ds.coords["lon"]
    except Exception as e:
        try:
            lats = ds.coords["latitude"]
            lons = ds.coords["longitude"]
        except Exception as e:
            click.echo(e)

    min_lat=min(lats).values
    min_lat_float=float(min_lat)
    min_lon=min(lons).values
    min_lon_float=float(min_lon)
    max_lat=max(lats).values
    max_lat_float=float(max_lat)
    max_lon=max(lons).values
    max_lon_float=float(max_lon)

    bbox = [min_lon_float,min_lat_float,max_lon_float,max_lat_float]
    extractTool.print_pretty_bbox(filepath,bbox, "NetCDF")
    ds.close()
    return bbox