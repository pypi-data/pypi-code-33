import click        # used to print something
import extractTool # used for the the transformation and prints  
import pandas as pd # to read the csv we use Pandas: http://pandas.pydata.org/pandas-docs/stable/io.html
import numpy as np  # used to calculate the convex hull
from scipy.spatial import ConvexHull  # used to calculate the convex hull
import dateparser   # used to parse the dates

"""
Function for extracting the spatial and temporal information of a csv file
:see: https://www.programiz.com/python-programming/reading-csv-files

:param filepath: path to the file
:param detail: specifies the level of detail of the geospatial extent (bbox or convex hull)
:param time: boolean variable, if it is true the user gets the temporal extent instead of the spatial extent
:returns: spatial and temporal information in the format [[bounding box],[convex Hull],[temporal extent]]
it is not possible to get the output of the bounding box and the convex hull
"""
def getCSVbbx(filepath, detail, time):
    # some identifiers used to compare them with the first line of the csv file
    list_lat_identifier = ["Koordinate_Hochwert","lat","Latitude","latitude","Lat"]
    list_lon_identifier = ["Koordinate_Rechtswert","lon","Lon","Longitude","longitude","lng","Lng"]
    list_crs = ["CRS","crs","Koordinatensystem","EPSG","Coordinate reference system", "coordinate system"]
    list_time = ["time", "timestamp", "date", "Time", "Jahr", "Datum", "Date", "Timestamp"]

    # try to read the csv
    df = csv_split(filepath)

    # tests if there is a column named coordinate reference system or similar       
    if intersect(list_crs,df.columns.values):
        CRSinfo= True
    else:
        CRSinfo= False

    # check if there are columns for latitude and longitude 
    if intersect(list_lat_identifier,df.columns.values) and intersect(list_lon_identifier,df.columns.values):
        # assign the lat and lon identifier
        my_lat=intersect(list_lat_identifier,df.columns.values)
        my_lon=intersect(list_lon_identifier,df.columns.values)
        # saves the coordinate values for latitude and longitude
        lats=df[my_lat[0]]
        lons=df[my_lon[0]]
        
        # invoce cvs_bbox if bbox is used as level of detail
        if detail =='bbox':
            bbox_val=csv_bbox(filepath, lats, lons, CRSinfo, df)
        else:
            bbox_val=[None]

        # invoce csv_convex_hull if convex hull is used as level of detail
        if detail == 'convexHull':
            convex_hull_val=csv_convex_hull(filepath , lats, lons, CRSinfo, df)
        else:
            convex_hull_val=[None]
    else:
        click.echo("No fitting header for latitudes,longitudes")
        bbox_val=[None]
        convex_hull_val=[None]

    # check if there are columns for time values 
    if intersect(list_time,df.columns.values):
        my_time_identifier=intersect(list_time,df.columns.values)
        # if time is used as a flag, invoke csv_time
        if (time):
            time_val=csv_time(filepath ,my_time_identifier,df)
        else:
            time_val=[None]
    else:
        my_time_identifier= False
        click.echo("No time information available")
        time_val=[None]

    ret_value=[bbox_val, convex_hull_val, time_val]
    return ret_value

"""
Function for splitting a csv file

:param filepath: path to the file
:raises: TypeError, if its not possible to read the file with ';' or ',' as a delimiter
:returns: datafile as a read_csv
"""
def csv_split(filepath):
    # Here we avoid that a gml is parsed as a csv 
    my_split=filepath.split('.')
    if(my_split[len(my_split)-1]=='gml'):
        raise TypeError("This is a gml and not a csv file!")
    try:
        deli=';'
        df = pd.read_csv(filepath, delimiter=deli,engine='python')
        return df
    except:
        try:
            deli=','
            df = pd.read_csv(filepath, delimiter=deli,engine='python')
            return df
        except:
            raise TypeError("This is not a csv file!")

"""
Function for extracting the temporal extent of the CSV file

:param filepath: path to the file
:param my_time_id: identifier of the time values
:param df: CSV reader
:returns: time, meeting the ISO8601 standard, in the form [time_min, time_max]
"""
def csv_time(filepath, my_time_id, df):
    if my_time_id:
        # get the identifier for time for this specific csv
        time=df[my_time_id[0]]
        # convert the min and max of time as a string
        time_min=str(min(time))
        time_max=str(max(time))
        # format the time
        time_max_formatted=str(dateparser.parse(time_max))
        time_min_formatted=str(dateparser.parse(time_min))

        time_extend=[time_min_formatted, time_max_formatted]
        # pretty print of time
        extractTool.print_pretty_time(filepath, time_extend,"CSV")
        return time_extend
    else:
        click.echo("No fitting header for time-values")
        return [None]

"""
Function for extracting the convex Hull

:param filepath: path to the file
:param my_lats: latitude values 
:param my_lons: longitude values
:param my_crs_info: identifier of the CRS info
:param df: CSV reader
:returns: convex hull of the csv with points in the form [lon,lat]
"""
def csv_convex_hull(filepath , my_lats, my_lons, my_crs_info, df):
    list_crs = ["CRS","crs","Koordinatensystem","EPSG","Coordinate reference system", "coordinate system"]
    coords=np.column_stack((my_lons, my_lats))
    # definition and calculation of the convex hull
    hull=ConvexHull(coords)
    hull_points=hull.vertices
    convex_hull=[]
    for z in hull_points:
        point=[coords[z][0], coords[z][1]]
        convex_hull.append(point)
        
    # coordinate transformation if we have information about the crs
    if(my_crs_info):
        my_crs_id=intersect(list_crs,df.columns.values)
        my_list_crs=df[my_crs_id[0]]
        my_crs=my_list_crs[0]
        for z in coords:
            z[0],z[1] = extractTool.transformToWGS84(z[0],z[1], my_crs)
        extractTool.print_pretty_hull(filepath, convex_hull,"CSV")
        return convex_hull
    else:
        extractTool.print_pretty_hull(filepath, convex_hull,"CSV")
        click.echo("Missing CRS -----> Boundingbox will not be saved in zenodo.")
        return None

"""
Function for extracting the bbox

:param filepath: path to the file
:param my_lats: latitude values 
:param my_lons: longitude values
:param my_crs_info: identifier of the CRS info
:param df: CSV reader
:returns: bounding box of the csv in the format [minlon, minlat, maxlon, maxlat]
"""
def csv_bbox(filepath , my_lats, my_lons, my_CRS_info, df):
    list_crs = ["CRS","crs","Koordinatensystem","EPSG","Coordinate reference system", "coordinate system"]
    bbox=[min(my_lons),min(my_lats),max(my_lons),max(my_lats)]
    
    # CRS transformation if there is information about crs
    if(my_CRS_info):
        my_crs_id=intersect(list_crs,df.columns.values)
        # values for the crs
        my_list_crs=df[my_crs_id[0]]
        # get the first crs id 
        my_crs=my_list_crs[0]
        lon_min_t, lat_min_t = extractTool.transformToWGS84(min(my_lons),min(my_lats), my_crs)
        lon_max_t, lat_max_t = extractTool.transformToWGS84(max(my_lons),max(my_lats), my_crs)
        bbox=[lon_min_t,lat_min_t,lon_max_t,lat_max_t]
        extractTool.print_pretty_bbox(filepath,bbox,"CSV")
        return bbox
    else:
        extractTool.print_pretty_bbox(filepath,bbox,"CSV")
        click.echo("Missing CRS -----> Boundingbox will not be saved in zenodo.")
        return [None]
        
"""
Auxiliary function for testing if an identifier for the temporal or spatial extent is part of the header in the csv file
:param a: collection of identifiers
:param b: collection of identifiers
:returns: equal identifiers
"""
def intersect(a, b):
     return list(set(a) & set(b))