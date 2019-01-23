#import click, json, sqlite3, csv, pygeoj
#from osgeo import gdal, ogr, osr
#import pandas as pd
#import numpy as np
#import xarray as xr
#import os
from pyproj import Proj, transform
import click
import getShapefileInfo, getGeoTiffInfo, getCSVInfo, getIsoInfo, getGeoJsonInfo, getNetCDFInfo, getGeoPackageInfo, openFolder

"""
global variable to save the bbox values of single files it is used for the boundingbox extraction of a whole folder
"""
#bboxArray = []
timeextendArray=[]
#ret_value=[]


"""
Auxiliary function to bypass problems with the CLI tool when executed from anywhere else

:param path: path to the directory of the files or to the file itself
:param detail: specifies the level of detail of the geospatial extent (bbox or convex hull)
:param folder: specifies if the user gets the metadata for the whole folder "whole" or for each file "single"
:param time: boolean variable, if it is true the user gets the temporal extent instead of the spatial extent

Function for extracting the metadata (bounding box)
An advantage of our code is that the file extension is not important for the metadataextraction but the content of the file

:param path: path to the directory of the files or to the file itself
:param detail: specifies the level of detail of the geospatial extent (bbox or convex hull)
:param folder: specifies if the user gets the metadata for the whole folder "whole" or for each file "single"
:param time: boolean variable, if it is true the user gets the temporal extent instead of the spatial extent
:returns: spatial extent as a bbox in the format [minlon, minlat, maxlon, maxlat]
"""

@click.command()
@click.option('--path',required=True,prompt='insert filepath!', help='please insert the path to the data here.')
@click.option('--time', is_flag=True, help='returns the time extend of one object')
@click.option('--detail', type=click.Choice(['bbox', 'convexHull']), default='bbox', help='select which information you want to get')
@click.option('--folder', type=click.Choice(['single', 'whole']), default='single', help='select if you want to get the Metadata from the whole folder or for each seperate file.')


def click_function(path, detail, folder, time):
    getMetadata(path, detail, folder, time)

def getMetadata(path, detail, folder, time):
   
    filepath = path
   
    # if(len(filepath)==0):
    #     click.echo("Please insert a correct filepath")
    #     return None
    try:
        click.echo("detailShape")
        a=getShapefileInfo.getShapefilebbx(filepath, detail, folder, time)
    except Exception as e:
        try:
            print("This is no valid Shapefile.")
            click.echo("detailjson")
            a=getGeoJsonInfo.getGeoJsonbbx(filepath, detail, folder, time)
        except Exception as e:
            try:
                print("error")
                print(e)
                click.echo("detail_netcdf")
                a=getNetCDFInfo.getNetCDFbbx(filepath, detail, folder, time)
            except Exception as e:
                try:
                    print("detail_csv")
                    a=getCSVInfo.getCSVbbx(filepath, detail, folder, time)
                except Exception as e:
                    try:
                        print e
                        print("detail geopackage")
                        a=getGeoPackageInfo.getGeopackagebbx(filepath, detail, folder, time)
                    except Exception as e:
                        try:
                            print (e)
                            print("neu")
                            click.echo("detail geotiff")
                            a=getGeoTiffInfo.getGeoTiffbbx(filepath, detail, folder, time)
                        except Exception as e:
                            try:
                                print(e)
                                click.echo("detailiso")
                                a=getIsoInfo.getIsobbx(filepath, detail, folder, time)
                            except Exception as e:
                                try:
                                    click.echo(e)
                                    click.echo("detail folder")
                                    a=openFolder.openFolder(filepath, detail, folder, time)
                                except Exception as e:
                                    #click.echo(e)
                                    #click.echo ("invalid file format!!!!!")
                                    #return 0
                                    a=None
    print("Final extraction:")
    print(a)
    return a

"""
Function for transforming the coordinate reference system to WGS84 using PyProj (https://github.com/jswhit/pyproj)

:param lat: value for latitude
:param lng: value for longitude
:sourceCRS: epsg identifier for the source coordinate reference system
:returns: the transformed values for latitude and longitude 
"""
def transformToWGS84(lat, lng, sourceCRS):
    # formatting the input CRS
    try:
        inputProj='epsg:'
        inputProj+=str(sourceCRS)
        inProj = Proj(init=inputProj)
        # epsg:4326 is WGS84
        outProj = Proj(init='epsg:4326')
        latT, lngT = transform(inProj,outProj,lat,lng)
        return(latT,lngT)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    click_function()
