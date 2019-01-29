import click        # used to print something 
import extractTool  # used for the the transformation and prints 
import pandas as pd # to read the csv we use Pandas: http://pandas.pydata.org/pandas-docs/stable/io.html
import numpy as np  # used to calculate the convex hull
from scipy.spatial import ConvexHull  # used to calculate the convex hull
import dateparser   # used to parse the dates
import sys

"""
Function for extracting the bounding box of a csv file
:see: https://www.programiz.com/python-programming/reading-csv-files

:param filepath: path to the file
:param detail: specifies the level of detail of the geospatial extent (bbox or convex hull)
:param folder: specifies if the user gets the metadata for the whole folder (whole) or for each file (single)
:param time: boolean variable, if it is true the user gets the temporal extent instead of the spatial extent
:returns: spatial extent as a bbox in the format [minlon, minlat, maxlon, maxlat]
"""
def getCSVbbx(filepath, detail, folder, time):
    # some identifiers for comparing them with the first line of the csv file
    listlat = ["Koordinate_Hochwert","lat","Latitude","latitude","Lat"]
    listlon = ["Koordinate_Rechtswert","lon","Lon","Longitude","longitude","lng","Lng"]
    listCRS = ["CRS","crs","Koordinatensystem","EPSG","Coordinate reference system", "coordinate system"]
    listtime = ["time", "timestamp", "date", "Time", "Jahr", "Datum", "Date", "Timestamp"]

    #click.echo("csv")
    # read the csv
    df = csv_split(filepath)

    #tests if there is a column named coordinate reference system or similar       
    if not intersect(listCRS,df.columns.values):
        CRSinfo= False
        click.echo("No fitting header for a reference system")
    else:
        CRSinfo= True
    # check if there are columns for latitude, longitude and timestamp
    if not(intersect(listlat,df.columns.values) and intersect(listlon,df.columns.values)):
        click.echo("No fitting header for latitudes,longitudes")
        #raise Exception('No fitting header for latitudes,longitudes')
        #lats, lons = None
    else:
        my_lat=intersect(listlat,df.columns.values)
        my_lon=intersect(listlon,df.columns.values)
        # saves the coordinate values for latitude and longitude
        lats=df[my_lat[0]]
        lons=df[my_lon[0]]

    if intersect(listtime,df.columns.values):
        my_time_identifier=intersect(listtime,df.columns.values)
    else:
        my_time_identifier= False
        click.echo("No time information available")

    # print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    if detail =='bbox':
        bbox_val=csv_bbox(filepath, folder, lats, lons, CRSinfo, df)

    else:
        bbox_val=[None]

    #returns the convex hull of the coordinates from the CSV object.
    if detail == 'convexHull':
        convHull_val=csv_convHull(filepath, folder, lats, lons, CRSinfo, df)

    else:
        convHull_val=[None]

    if (time):
        time_val=csv_time(filepath, folder,my_time_identifier,df)
    else:
        time_val=[None]
    
    #if folder=='single':
    ret_value=[bbox_val, convHull_val, time_val]
    # print(ret_value)
    return ret_value

"""
Function for splitting a csv file

:param filepath: path to the file
:returns: datafile as a read_csv
"""
def csv_split(filepath):
    # print("in split")
    # First try ';' as the delimiter, if that does not work, take ','
    try:
        deli=';'
        df = pd.read_csv(filepath, delimiter=deli,engine='python') 
        
    except Exception:
        deli=','
        df = pd.read_csv(filepath, delimiter=deli,engine='python')
    return df

"""
Function for extracting the temporal extent of the CSV file

:param filepath: path to the file
:param folder: specifies if we have a single file or a folder
:param my_time_id: identifier of the time values
:param df: CSV reader
:returns: datafile as a read_csv
"""
def csv_time(filepath, folder, my_time_id, df):
    if my_time_id:
        time=df[my_time_id[0]]
        # print(min(time))
        # print(max(time))
        timemin=str(min(time))
        timemax=str(max(time))
        timemax_formatted=str(dateparser.parse(timemax))
        timemin_formatted=str(dateparser.parse(timemin))
        timeextend=[timemin_formatted, timemax_formatted]
        # print(timeextend)
        #if folder=='single':
        extractTool.print_pretty_time(filepath, timeextend,"CSV")
        return timeextend
        #if folder=='whole':
        #    extractTool.timeextendArray.append(filepath, timeextend)
        #    print("timeextendArray:")
        #    print(extractTool.timeextendArray)
    else:
        print("No fitting header for time-values")
        return [None]

"""
Function for extracting the convex Hull

:param filepath: path to the file
:param folder: specifies if we have a single file or a folder
:param my_lats: latitude values 
:param my_lons: longitude values
:param my_CRSinfo: identifier of the CRS info
:param df: CSV reader
:returns: convex hull of the csv
"""
def csv_convHull(filepath, folder, my_lats, my_lons, my_CRSinfo, df):
    listCRS = ["CRS","crs","Koordinatensystem","EPSG","Coordinate reference system", "coordinate system"]
    click.echo("convexHull")
    coords=np.column_stack((my_lats, my_lons))
    #definition and calculation of the convex hull
    hull=ConvexHull(coords)
    hull_points=hull.vertices
    convHull=[]
    for z in hull_points:
        point=[coords[z][0], coords[z][1]]
        convHull.append(point)
    if(my_CRSinfo):
        mycrsID=intersect(listCRS,df.columns.values)
        myCRS=df[mycrsID[0]]
        myCRS_1=myCRS[0]
        # print(myCRS_1)
        for z in coords:
            z[0],z[1] = extractTool.transformToWGS84(z[0],z[1], myCRS_1)
        #if folder=='single':
        extractTool.print_pretty_hull(filepath, convHull,"CSV")
        return convHull
        #if folder=='whole':
        #    extractTool.bboxArray=extractTool.bboxArray+convHull
        #    extractTool.print_pretty_hull(filepath, convHull,"CSV")
            #return convHull
    else:
        #if folder=='single':
        extractTool.print_pretty_hull(filepath, convHull,"CSV")
        click.echo("Missing CRS -----> Boundingbox will not be saved in zenodo.")
        return None
        #if folder=='whole':
        #    extractTool.print_pretty_hull(filepath, convHull,"CSV")
        #    click.echo("because of a missing crs this CSV is not part of the folder calculation.")

"""
Function for extracting the bbox

:param filepath: path to the file
:param folder: specifies if we have a single file or a folder
:param my_lats: latitude values 
:param my_lons: longitude values
:param my_CRSinfo: identifier of the CRS info
:param df: CSV reader
:returns: bounding box of the csv
"""
def csv_bbox(filepath, folder, my_lats, my_lons, my_CRS_info, df):
    listCRS = ["CRS","crs","Koordinatensystem","EPSG","Coordinate reference system", "coordinate system"]
    bbox=[min(my_lats),min(my_lons),max(my_lats),max(my_lons)]
    # print("BBOX")
    # print(bbox)
    # CRS transformation if there is information about crs
    if(my_CRS_info):
        mycrsID=intersect(listCRS,df.columns.values)
        myCRS=df[mycrsID[0]]
        myCRS1=myCRS[0]
        # print(myCRS1)
        lat1t,lng1t = extractTool.transformToWGS84(min(my_lats),min(my_lons), myCRS1)
        lat2t,lng2t = extractTool.transformToWGS84(max(my_lats),max(my_lons), myCRS1)
        bbox=[lat1t,lng1t,lat2t,lng2t]
        #if folder=='single':
        extractTool.print_pretty_bbox(filepath,bbox,"CSV")
        return bbox
        #if folder=='whole':
        #    extractTool.bboxArray.append(bbox)
        #    extractTool.print_pretty_bbox(filepath,bbox,"CSV")

    else:
        #if folder=='single':
        extractTool.print_pretty_bbox(filepath,bbox,"CSV")
        print("Missing CRS -----> Boundingbox will not be saved in zenodo.")
        return [None]
        #if folder=='whole':
        #    extractTool.print_pretty_bbox(filepath,bbox,"CSV")
        #    click.echo("because of a missing crs this CSV is not part of the folder calculation.")

"""
Auxiliary function for testing if an identifier for the temporal or spatial extent is part of the header in the csv file
:param a: collection of identifiers
:param b: collection of identifiers
:returns: equal identifiers
"""
def intersect(a, b):
     return list(set(a) & set(b))
