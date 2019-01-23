import click,json, sqlite3, pygeoj, csv
from osgeo import gdal, ogr, osr
import pandas as pd
import numpy as np
import extractTool
from scipy.spatial import ConvexHull
import dateparser
from pyproj import Proj, transform
#import sys

#import ogr2ogr
#ogr2ogr.BASEPATH = "/home/caro/Vorlagen/Geosoftware2/Metadatenextraktion"

listlat = ["Koordinate_Hochwert","lat","Latitude","latitude"]
listlon = ["Koordinate_Rechtswert","lon","Longitude","longitude","lng"]
listCRS = ["CRS","crs","Koordinatensystem","EPSG","Coordinate reference system", "coordinate system"]
listtime = ["time", "timestamp", "date", "Time", "Jahr", "Datum"]


"""
Function for extracting the bounding box of a csv file
@see https://www.programiz.com/python-programming/reading-csv-files

:param filepath: path to the file
:param detail: specifies the level of detail of the geospatial extent (bbox or convex hull)
:param folder: specifies if the user gets the metadata for the whole folder (whole) or for each file (single)
:param time: boolean variable, if it is true the user gets the temporal extent instead of the spatial extent
:returns: spatial extent as a bbox in the format [minlon, minlat, maxlon, maxlat]
"""

def getCSVbbx(filepath, detail, folder, time):
    #format validation
    pd.read_csv(filepath)
    click.echo("csv")
    
    if detail =='bbox':
        bbox_val=csv_bbox(filepath, folder)

    else:
        bbox_val=[None]

    #returns the convex hull of the coordinates from the CSV object.
    if detail == 'convexHull':
        convHull_val=csv_convHull(filepath, folder)

    else:
        convHull_val=[None]
    if (time):
        time_val=csv_time(filepath, folder)

    else:
        time_val=[None]
    
    #if folder=='single':
    ret_value=[bbox_val, convHull_val, time_val]
    print(ret_value)
    return ret_value

def csv_split(filepath):
    CRSinfo=True
    print("in split")
    try:
        deli=';'
        df = pd.read_csv(filepath, delimiter=deli,engine='python')
        #tests if there is a column named Coordinatesystem or similar
        if not intersect(listCRS,df.columns.values):
            CRSinfo= False
            print("No fitting header for a reference system1")

        if not(((intersect(listlat,df.columns.values) and intersect(listlon,df.columns.values)))or (intersect(listtime, df.columns.values))):
            #output="No fitting header for latitudes or longitudes"
            raise Exception('No fitting ')
            #return output
        
        return [deli, CRSinfo]
        

    except Exception as exce:
        CRSinfo=True
        deli=','
        df = pd.read_csv(filepath, delimiter=deli,engine='python')
        #tests if there is a column named Coordinatesystem or similar
        #click.echo("hi")
        #click.echo(df.columns.values)
        #click.echo(intersect(listCRS,df.columns.values))
        if not intersect(listCRS,df.columns.values):
            CRSinfo= False
            
            print("No fitting header for a reference system2")
            z=intersect(listtime, df.columns.values)
            print (z)
            t=intersect(listlat,df.columns.values) and intersect(listlon,df.columns.values)
            print (intersect(listlat,df.columns.values))
            print(t)
            if not t:
                print("false")

        if not(((intersect(listlat,df.columns.values) and intersect(listlon,df.columns.values)))or (intersect(listtime, df.columns.values))):
            #output="No fitting header for latitudes or longitudes"
            #raise Exception('No fim')
        
            raise Exception("evtl kein csv oder ungueltiges Trennzeichen.")
            #print("keine Koordinaten vorhanden")
            #print(output)
            #return output#
        
        #print(deli)
        print("++++++++++++++++++")
        return [deli, CRSinfo]
        #print (exce)


def csv_time(filepath, folder):
    click.echo("hallo")
    # Using Pandas: http://pandas.pydata.org/pandas-docs/stable/io.html
    deli=csv_split(filepath)[0]
    CRSinfo=csv_split(filepath)[1]
    df = pd.read_csv(filepath, delimiter=deli,engine='python')
    #df=csv_split(filepath)
    click.echo(listtime)
    click.echo(df.columns.values)
    intersection=intersect(listtime, df.columns.values)
    click.echo(intersection)
    if not intersection:
        print("No fitting header for time-values")
        return [None]
        # TODO: fehlerbehandlung  
        #try:
            #for t in listtime:
                #if(x not in df.columns.values):
                    #click.echo("This file does not include time-values")
                #else:
                    #time=df[t]
                    #timeextend =[min(time), max(time)]
                    #click.echo(timeextend)
                    #return timeextend
        #except Exception as e:
            #click.echo ("There is no time-value or invalid file.")
            #return None   
    else:
        
        
        time=df[intersection[0]]
        print(min(time))
        print(max(time))
        timemin=str(min(time))
        timemax=str(max(time))
        timemax_formatted=dateparser.parse(timemax)
        timemin_formatted=dateparser.parse(timemin)
        timeextend=[timemin_formatted, timemax_formatted]
        print(timeextend)
        #if folder=='single':
        print("----------------------------------------------------------------")
        click.echo("Timeextend of this CSV file:")
        click.echo(timeextend)
        print("----------------------------------------------------------------")
        return timeextend
        #if folder=='whole':
        #    extractTool.timeextendArray.append(timeextend)
        #    print("timeextendArray:")
        #    print(extractTool.timeextendArray)


def csv_convHull(filepath, folder):
    #df=csv_split(filepath)
    deli=csv_split(filepath)[0]
    CRSinfo=csv_split(filepath)[1]

    df = pd.read_csv(filepath, delimiter=deli,engine='python')

    click.echo("convexHull")
    mylat=intersect(listlat,df.columns.values)
    mylon=intersect(listlon,df.columns.values)
    lats=df[mylat[0]]
    lons=df[mylon[0]]
    coords=np.column_stack((lats, lons))
    #definition and calculation of the convex hull
    hull=ConvexHull(coords)
    hull_points=hull.vertices
    convHull=[]
    for z in hull_points:
        point=[coords[z][0], coords[z][1]]
        convHull.append(point)
    if(CRSinfo):
        mycrsID=intersect(listCRS,df.columns.values)
        myCRS=df[mycrsID[0]]
        inputProj='epsg:'
        inputProj+=str(myCRS[0])
        print(inputProj)
        inProj = Proj(init=inputProj)
        outProj = Proj(init='epsg:4326')
        for z in coords:
            z[0],z[1] = transform(inProj,outProj,z[0],z[1])
        # if folder=='single':
        print("----------------------------------------------------------------")
        click.echo("Filepath:")
        click.echo(filepath)
        click.echo("convex Hull of the csv file: ")
        click.echo(convHull)
        print("----------------------------------------------------------------")
        return convHull
        # if folder=='whole':
        #     extractTool.bboxArray=extractTool.bboxArray+convHull
        #     print("----------------------------------------------------------------")
        #     click.echo("Filepath:")
        #     click.echo(filepath)
        #     click.echo("convex hull of the CSV:")
        #     click.echo(convHull)
        #     print("----------------------------------------------------------------")
        #     #return convHull
    else:
        # if folder=='single':
        print("----------------------------------------------------------------")
        click.echo("Filepath:")
        click.echo(filepath)
        click.echo("Convex hull of the CSV object:")
        print(convHull)
        print("Missing CRS -----> Boundingbox will not be saved in zenodo.")
        print("----------------------------------------------------------------")
        return None
        # if folder=='whole':
        #     print("----------------------------------------------------------------")
        #     click.echo("Filepath:")
        #     click.echo(filepath)
        #     click.echo("Convex hull of the CSV file:")
        #     click.echo(convHull)
        #     click.echo("because of a missing crs this CSV is not part of the folder calculation.")
        #     print("----------------------------------------------------------------")



def csv_bbox(filepath, folder):
    print("bbo")
    #df=csv_split(filepath)[0]
    deli=csv_split(filepath)[0]
    CRSinfo=csv_split(filepath)[1]
    print("hu")
    df = pd.read_csv(filepath, delimiter=deli,engine='python')
    print("###########################")
    print(df)

    #print(df)
    click.echo("bbox")
    # Using Pandas: http://pandas.pydata.org/pandas-docs/stable/io.html
    #if folder=='single':
    mylat=intersect(listlat,df.columns.values)
    mylon=intersect(listlon,df.columns.values)
    print mylat
    print(df[mylat[0]])
    print(df[mylon[0]])
    lats=df[mylat[0]]
    lons=df[mylon[0]]
    print("1")
    bbox=[min(lats),min(lons),max(lats),max(lons)]
    print("2")
    # CRS transformation if there is information about crs
    if(CRSinfo):
        print("3")
        mycrsID=intersect(listCRS,df.columns.values)
        print("4")
        print(df)
        print(CRSinfo)
        myCRS=df[mycrsID[0]]
        print("5")
        lat1t,lng1t = extractTool.transformToWGS84(min(lats),min(lons), myCRS)
        lat2t,lng2t = extractTool.transformToWGS84(max(lats),max(lons), myCRS)
        bbox=[lat1t,lng1t,lat2t,lng2t]
        #if folder=='single':
        print("----------------------------------------------------------------")
        click.echo("Filepath:")
        click.echo(filepath)
        click.echo("Boundingbox of the CSV object:")
        click.echo(bbox)
        print("----------------------------------------------------------------")
        return bbox
        # if folder=='whole':
        #     extractTool.bboxArray.append(bbox)
        #     print("----------------------------------------------------------------")
        #     click.echo("Filepath:")
        #     click.echo(filepath)
        #     click.echo("Boundingbox of the CSV:")
        #     click.echo(bbox)
        #     print("----------------------------------------------------------------")
    else:
        # if folder=='single':
        print("----------------------------------------------------------------")
        click.echo("Filepath:")
        click.echo(filepath)
        click.echo("Boundingbox of the CSV object:")
        print(bbox)
        print("Missing CRS -----> Boundingbox will not be saved in zenodo.")
        print("----------------------------------------------------------------")
        return [None]
        # if folder=='whole':
        #     print("----------------------------------------------------------------")
        #     click.echo("Filepath:")
        #     click.echo(filepath)
        #     click.echo("Boundingbox of the CSV file:")
        #     click.echo(bbox)
        #     click.echo("because of a missing crs this CSV is not part of the folder calculation.")
        #     print("----------------------------------------------------------------")


"""
Auxiliary function for testing if an identifier for the temporal or spatial extent is part of the header in the csv file
:param a: collection of identifiers
:param b: collection of identifiers
:returns: equal identifiers
"""
def intersect(a, b):
     return list(set(a) & set(b))
