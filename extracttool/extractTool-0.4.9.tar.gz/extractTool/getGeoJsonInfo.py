import click        # used to print something 
import pygeoj       # used to parse the geojson file, NOTE: only works with two-dimensional coordinates
import json         # used to parse the geojson file
import extractTool  # used for the the transformation and prints
import dateparser   # used to parse the dates   
from scipy.spatial import ConvexHull # used to compute the convex hull

# list which saves the points
point = list()

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
Function for extracting the spatial and temporal information of a geojson file 
As mentioned in the geojson specification the standard crs is wgs84.
:see:   https://tools.ietf.org/html/rfc7946#section-4

:param filepath: path to the file
:param detail: specifies the level of detail of the geospatial extent (bbox or convex hull)
:param time: boolean variable, if it is true the user gets the temporal extent instead of the spatial extent
:returns: spatial and temporal information in the format [[bounding box],[convex Hull],[temporal extent]]
"""
def getGeoJsonbbx(filepath, detail, time):
    if detail =='bbox':
        bbox_val=geojson_bbox(filepath)
    else:
        bbox_val=[None]

    if detail == 'convexHull':
        convex_hull_val=geojson_convex_hull(filepath)
    else:
        convex_hull_val=[None]

    if (time):
        time_val=geojson_time(filepath)
    else:
        time_val=[None]

    ret_value=[bbox_val, convex_hull_val, time_val]
    return ret_value

"""
Function for extracting the temporal extent of a geojson file

:param filepath: path to the file
:returns: time, meeting the ISO8601 standard, in the form [time_min, time_max]
"""
def geojson_time(filepath):
    # opening the file
    ds = open(filepath)
    # check if the file has the right format
    geojson = json.load(ds)
    time_list = list()
    if geojson["type"] == "FeatureCollection":
        first = geojson["features"]
        # Search for words like date, creationDate or time at two different levels
        for time in geojson: 
            try:
                time = first[0]["Date"]
                time_list.append(time)
            except Exception as e:
                try:
                    time = time[0]["creationDate"]
                    time_list.append(time)
                except Exception as e:
                    try:
                        time = first[0]["date"]
                        time_list.append(time)
                    except Exception as e:
                        try:
                            time = first[0]["time"]
                            time_list.append(time)
                        except Exception as e:
                            try:
                                time = first[0]["properties"]["date"]
                                time_list.append(time)
                            except Exception as e:
                                try:
                                    time = first[0]["properties"]["time"]
                                    time_list.append(time)
                                except Exception as e:
                                    try:
                                        time = first[0]["geometry"][0]["properties"]["STAND_DER_DATEN"]
                                        time_list.append(time)
                                    except Exception as e:
                                        click.echo("there is no time-value")
                                        return [None]
    # convert the min and max of time as a string
    time_max = str(max(time_list))
    time_min = str(min(time_list))
    # format the time
    time_max_formatted=str(dateparser.parse(time_max))
    time_min_formatted=str(dateparser.parse(time_min))
  
    timeextend = [time_min_formatted, time_max_formatted]
    extractTool.print_pretty_time(filepath, timeextend, "GeoJSON")
    return[time_max_formatted, time_min_formatted]

"""
Function for extracting the bbox using pygeoj

:param filepath: path to the file
:returns: bounding box of the geojson in the format [minlon, minlat, maxlon, maxlat]
"""
def geojson_bbox(filepath):
    geojson = pygeoj.load(filepath)
    bbox = (geojson).bbox
    extractTool.print_pretty_bbox(filepath, bbox, "GeoJSON")
    return bbox

"""
Function for extracting the convex hull

:param filepath: path to the file
:returns: convex hull of the geojson
"""
def geojson_convex_hull(filepath):
    geojson = pygeoj.load(filepath)
    for feature in geojson:
        try:
            coordinate_field= feature.geometry.coordinates
            extract_coordinates(coordinate_field)
        except Exception as e:
            click.echo(e)
            click.echo("Feature without coordinates in the geojson.")
        
    # Calculation of the convex hull
    hull=ConvexHull(point)
    hull_points=hull.vertices
    convex_hull=[]
    for z in hull_points:
        hullcoord=[point[z][0], point[z][1]]
        convex_hull.append(hullcoord)
    extractTool.print_pretty_hull(filepath, convex_hull, "GeoJSON")
    return convex_hull