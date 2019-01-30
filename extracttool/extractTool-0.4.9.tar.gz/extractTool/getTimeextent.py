# @author Carolin Bronowicz
# @version 1.0
# Tests for our getTimeextend file. This file is just for testing. The single fuctions are included in our extractTool.py 
import click        # used to print something
import shapefile, sqlite3, csv, json, pygeoj
from osgeo import gdal, ogr, osr
import os
import pandas as pd
import numpy as np
import xarray as xr
import ogr2ogr
import json
import dateparser   # used to parse the dates

timeextendArray=[]

"""
Function for extracting the temporal extent of filees
if this file cannot find any time-values the file throws an 
"invalid file format or no time-values included!" exception

:param path: path to the file
:param detail: specifies if the user wants the time as a level of detail 
:param folder: specifies if the user gets the metadata for the whole folder (whole) or for each file (single)
:returns: temporal extent 
"""
def getTimeextent(path, detail ):
    filepath = path
    try:
        getShapefiletime(filepath, detail)
    except Exception:
        try:
            getCSVtime(filepath, detail )
        except Exception:
            try:
                getNetCDFtime(filepath, detail)
            except Exception:
                try:
                    getGeopackagetime(filepath, detail)
                except Exception:
                    try: 
                        getGeoTifftime(filepath, detail)    
                    except Exception:
                        try:
                            getGeoJsontime(filepath, detail)
                        except Exception:
                            try: 
                                getIsoTime(filepath, detail)    
                            except Exception:
                                click.echo ("invalid file format or no time-values included!")

"""
Function for extracting the temporal extent of a shapefile
Shapefilesoes not have any time information so we return none

:param filepath: path to the file
:param detail: specifies if the user wants the time as a level of detail
:returns: None
"""
def getShapefiletime(filepath, detail):
    click.echo("Shapefile")
    click.echo(detail)
    if detail =='time':
        click.echo("There is no time-value for shapefiles")
        return None

"""
Function for extracting the temporal extent of a GeoTIFF
Because we havent seen any testdata with time values included, we asume or we rather commit that there are no time values

:param filepath: path to the file
:param detail: specifies if the user wants the time as a level of detail
"""
def getGeoTifftime(filepath, detail):
    """Because we havent seen any testdata with time values included, 
    we asume or we rather commit that there are no time values"""
    gdal.UseExceptions()
    click.echo("GeoTiff")
    if detail =='time':
        ds = gdal.Open(filepath)
        gdal.Info(ds)
        click.echo("there is no time value for GeoTIFF files")
        return None

"""
Function for extracting the temporal extent of a CSV file

:param filepath: path to the file
:param detail: specifies if the user wants the time as a level of detail
"""
def getCSVtime(filepath, detail):
    # After opening the file we search in the header for collumns with names like
    # date, time or timestamp. If some of these collumns exists we collect
    # all the values from inside and calculate the min and max
    # Doesn't work if there are empty lines 
    if detail =='time':
        # Using Pandas: http://pandas.pydata.org/pandas-docs/stable/io.html
        df = pd.read_csv(filepath, sep=';|,',engine='python')
        listtime = ["time", "timestamp", "date", "Time", "Jahr", "Datum"]
        click.echo(listtime)
        click.echo(df.columns.values)
        intersection=intersect(listtime, df.columns.values)
        click.echo(intersection)
        if not intersection:
            print("No fitting header for time-values")
        else:
            time=df[intersection[0]]
            timeextend=[min(time), max(time)]
            if folder=='single':
                print("----------------------------------------------------------------")
                click.echo("Timeextend of this CSV file:")
                click.echo(timeextend)
                print("----------------------------------------------------------------")
                return timeextend
            if folder=='whole':
                timeextendArray.append(timeextend)
                print("timeextendArray:")
                print(timeextendArray)

"""
Auxiliary function for testing if an identifier for the temporal or spatial extent is part of the header in the csv file
:param a: collection of identifiers
:param b: collection of identifiers
:returns: equal identifiers
"""
def intersect(a, b):
    return list(set(a) & set(b))

"""
Function for extracting the temporal extent of a GeoJSON

:param filepath: path to the file
:param detail: specifies if the user wants the time as a level of detail
:returns: temporal extent 
"""
def getGeoJsontime(filepath, detail):
    # After opening the file check if the file seems to have the right format
    # Then we search for words like date, creationDate or time at two different levels
    print("GeoJson")
    if detail =='time':
        ds = open(filepath)
        geojson = json.load(ds)
        print(" ")
        print("The time value of this file is:")
        timelist = list()
        if geojson["type"] == "FeatureCollection":
            first = geojson["features"]
            for time in geojson: 
                try:
                    time = first[0]["Date"]
                    timelist.append(time)
                except Exception as e:
                    try:
                        time = time[0]["creationDate"]
                        timelist.append(time)
                    except Exception as e:
                        try:
                            time = first[0]["date"]
                            timelist.append(time)
                        except Exception as e:
                            try:
                                time = first[0]["time"]
                                timelist.append(time)
                            except Exception as e:
                                try:
                                    time = first[0]["properties"]["date"]
                                    timelist.append(time)
                                except Exception as e:
                                    try:
                                        time = first[0]["properties"]["time"]
                                        timelist.append(time)
                                    except Exception as e:
                                        try:
                                            time = first[0]["geometry"][0]["properties"]["STAND_DER_DATEN"]
                                            timelist.append(time)
                                        except Exception as e:
                                            click.echo("there is no time-value")
                                            return None         
        timemax = min(timelist)
        timemin = max(timelist)
        click.echo(max(timelist))
        return timemax

"""
Function for extracting the temporal extent of a NetCDF file

:param filepath: path to the file
:param detail: specifies if the user wants the time as a level of detail
:returns: temporal extent 
"""
def getNetCDFtime(filepath, detail):
    click.echo("NetCDF")
    if detail =='time':
        # opening the file as an xarray, @see: http://xarray.pydata.org/en/stable/index.html
        ds = xr.open_dataset(filepath)
        try:
            mytime = ds.coords["time"]
            starttime = min(mytime)
            endtime = max(mytime)
            # temporal extent
            start = str(starttime.values)
            end = str(endtime.values)
            timemax_formatted=dateparser.parse(start)
            timemin_formatted=dateparser.parse(end)
            return [start, end]
        except Exception as e:
            click.echo ("There is no time-value or invalid file")
            return None

"""
Function for extracting the temporal extent of a Geopackage file
Geopackages do not have any time information so we return None

:param filepath: path to the file
:param detail: specifies if the user wants the time as a level of detail
:returns: None
"""
def getGeopackagetime(filepath, detail):
    if detail =='time':
        click.echo ("There is no time-value for Geopackage files")
        return None
        
"""
Function for extracting the temporal extent of an iso file
:param filepath: path to the file
:param detail: specifies if the user wants the time as a level of detail
:returns: temporal extent
"""
def getIsoTime(filepath, detail):
    if detail =='time':
        # We transform the gml file to a geojson file
        ogr2ogr.main(["","-f", "GeoJSON", "time.json", filepath])
        iso = open("time.json")
        geojson = json.load(iso)
        # @see https://www.w3schools.com/python/python_file_remove.asp
        os.remove("time.json")
        # search for words like "Date", "creationDate", "time" and collect them
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
                                            time = first[i]["properties"]["Date"]
                                            return time
                                        except Exception as e:
                                            click.echo("there is no time-value")
                                            return None   
            return time

if __name__ == '__main__':
    getTimeextent()