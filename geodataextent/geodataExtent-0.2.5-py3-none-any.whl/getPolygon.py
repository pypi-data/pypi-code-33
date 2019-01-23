'''
Created on 29.10.2018
@author: Henry Fock, Lia Kirsch
'''

import csv
import os
import sys
import sqlite3
import tempfile
from geodataExtent import getBoundingBox

# add local modules folder
# file_path = os.path.join('..', 'Python_Modules')
# sys.path.append(file_path)

from osgeo import ogr, osr
import click
import pandas as pd
import pygeoj
import shapefile
import ogr2ogr


# asking for parameters in command line
@click.command()
@click.option('--path', prompt="File path", help='Path to file')
@click.option('--name', prompt="File name", help="File name with extension")
@click.option('--clear', '-c', default=False, is_flag=True, help='Clear screen before showing results')
def main(path, name, clear):
    res = getPolygon(name, path)
    if clear:
        click.clear()
    if res[0] is not None:
        click.echo(res[0])
    else:
        click.echo(res[1])


def getPolygon(name, path):
    """returns the Convex Hull of supported Datatypes and standards in WGS84.

    supported data: Shapefile (.shp), GeoJson (.json/.geojson), GeoTIFF (.tif), netCDF (.nc), GeoPackage (.gpkg), all ISO19xxx standardised formats and CSV on the web

    @param path Path to the file
    @param name name of the file with extension
    @returns a Convex Hull in first place of a tuple as Array. Points in WGS84 ([(long, lat), (long, lat), ...], None)
    """

    # connect name and path to file
    filepath = os.path.join(path, name)
    # get file extension
    filename, file_extension = os.path.splitext(filepath)

#################################################################

    def shapefileCase(filepath):
        """Method for extracting the convex hull of a shapefile
        @param filepath Full path to shapefile
        @returns a tuple where in first place is the convex hull as an array of point tuples
        """
        try:
            dataset = ogr.Open(filepath)
            layer = dataset.GetLayer()
            crs = layer.GetSpatialRef()
            if crs.IsProjected() == 1:
                crs = int(crs.GetAttrValue("PROJCS|AUTHORITY", 1))
            elif crs.IsGeographic() == 1:
                crs = int(crs.GetAttrValue("GEOGCS|AUTHORITY", 1))
            else:
                return (None, "CRS is missing!")

            myshp = open(filepath, "rb")
            sf = shapefile.Reader(shp=myshp)
            shapes = sf.shapes()
            pointList = []
            for shape in shapes:
                for points in shape.points:
                    pointList.append(
                        tuple(CRSTransform(points[1], points[0], crs)))
        # error
        except:
            return (None, "File Error!")
        else:  # if no error accured
            return (convex_hull(pointList), None)

    def jsonCase(filepath):
        """Method for extracting the convex hull of a GeoJSON file
        @param filepath Full path to GeoJSON file
        @returns a tuple where in first place is the convex hull as an array of point tuples
        """
        try:
            myGeojson = pygeoj.load(filepath=filepath)
            pointList = []

            for features in myGeojson:
                pointList.extend(
                    list(map(tuple, getCoordinatesFromGeoJson(features.geometry.coordinates))))

            return (convex_hull(pointList), None)
        # errors
        except:
            return (None, "File Error!")

    def ncTiffCase(name, path):
        """Method for extracting the convex hull of a netCDF file
        @param filepath Full path to netCDF file
        @returns a tuple where in first place is the convex hull as an array of point tuples
        """
        bbox = getBoundingBox.getBoundingBox(name, path)
        if bbox[1] is None:
            return ([(bbox[0][0], bbox[0][1]), (bbox[0][0], bbox[0][3]), (bbox[0][2], bbox[0][3]), (bbox[0][2], bbox[0][1])], None)
        else:
            return bbox

    def geoPackageCase(filepath):
        """Method for extracting the convex hull of a GeoPackage
        @param filepath Full path to GeoPackage
        @returns a tuple where in first place is the convex hull as an array of point tuples
        @see https://stackoverflow.com/questions/35945437/python-gdal-projection-conversion-from-wgs84-to-nztm2000-is-not-correct
        """
        try:
            conn = sqlite3.connect(filepath)
            c = conn.cursor()
            c.execute("""   SELECT min_x, min_y, max_x, max_y, srs_id
                            FROM gpkg_contents
                            WHERE NOT srs_id = 4327 OR srs_id = 4328
                    """)
            row = c.fetchall()
            bboxes = []

            if row is None:
                raise LookupError(
                    "No valid data detected (check if CRS maybe depracted)")

            for line in row:
                if not any(x is None for x in line):
                    bboxes.append(
                        [line[0], line[1], line[2], line[3], line[4]])

            if bboxes == []:
                raise LookupError(
                    "No valid data detected! Coordinates in gpkg_contents are invalid")

            wgs84points = []
            for bbox in bboxes:
                wgs84points.append(CRSTransform(bbox[0], bbox[1], bbox[4]))
                wgs84points.append(CRSTransform(bbox[0], bbox[3], bbox[4]))
                wgs84points.append(CRSTransform(bbox[2], bbox[1], bbox[4]))
                wgs84points.append(CRSTransform(bbox[2], bbox[3], bbox[4]))

            return(convex_hull(wgs84points), None)

        except LookupError as e:
            return(None, e)
        except:
            return (None, "File Error!")
        finally:
            try:
                conn.close()
            except:
                pass

    def csvCase(filepath):
        """Method for extracting the convex hull of a CSV file
        @param filepath Full path to CSV file
        @returns a tuple where in first place is the convex hull as an array of point tuples
        @see https://stackoverflow.com/questions/16503560/read-specific-columns-from-a-csv-file-with-csv-module
        """
        try:  # finding the correct columns for latitude and longitude
            csvfile = open(filepath)
            head = csv.reader(csvfile, delimiter=' ', quotechar='|')
            # get the headline an convert, if possible, ';' to ','
            # and seperate each word devided by a ',' into an array
            header = next(head)[0].replace(";", ",").split(",")

            # searching for valid names for latitude and longitude
            def getLatLonCrs(header):
                """get the correct names of the columns holding the coordinates
                @param header Header of the CSV
                @returns (lon, lat, crs) where lon, lat, crs are the column names
                """
                lng = None
                lat = None
                crs = None
                for t in header:
                    if t.lower() in ("longitude", "lon", "long", "lng"):
                        lng = t
                    if t.lower() in ("latitude", "lat"):
                        lat = t
                    if t.lower() in ("crs", "srs", "coordinate reference systems", "reference systems", "spatial reference system"):
                        crs = t
                return (lng, lat, crs)

            lng, lat, crs = getLatLonCrs(header)

            # if there is no valid name or coordinates, an exception is thrown an cought with an errormassage
            if(lat is None or lng is None):
                raise ValueError(
                    "pleas rename latitude an longitude: latitude/lat, longitude/lon/lng")
            if(crs is None):
                raise ValueError(
                    "please provide the coordinate reference systems. Name: crs/srs/coordinate reference systems/reference systems")

        # errors
        except ValueError as e:
            return (None, e)
        except:
            return (None, "File Error!")

        # if no error accured
        else:
            try:
                df = pd.read_csv(filepath, header=0)
                # get all coordinates from found columns
                latitudes = df[lng].tolist()
                longitudes = df[lat].tolist()
                srs = df[crs].tolist()

            # in case the words are separated by a ';' insted of a comma
            except KeyError:
                try:
                    # tell the reader that the seperator is a ';'
                    df = pd.read_csv(filepath, header=0, sep=';')
                    # get all coordinates from found columns
                    latitudes = df[lng].tolist()
                    longitudes = df[lat].tolist()
                    srs = df[crs].tolist()

                # the csv is not valid
                except KeyError:
                    return (None, "Pleas seperate your data with either ',' or ';'!")

            # errors
            except:
                return (None, "File Error: File not found or check if your csv file is valid to 'csv on the web'")

            pointList = []
            for i in range(len((latitudes))):
                pointList.append(
                    tuple(CRSTransform(longitudes[i], latitudes[i], crs[0])))

            return (convex_hull(pointList), None)

    def ISOCase(filepath):
        """Method for extracting the convex hull of an ISO19xxx standardized file
        @param filepath Full path to ISO19xxx standardized file
        @returns a tuple where in first place is the convex hull as an array of point tuples
        """
        try:
            # @see https://gis.stackexchange.com/questions/39080/using-ogr2ogr-to-convert-gml-to-shapefile-in-python
            # convert the gml file to a GeoJSON file
            with tempfile.TemporaryDirectory() as tmpdirname:
                curDir = os.getcwd()
                os.chdir(tmpdirname)
                ogr2ogr.main(["", "-f", "GeoJSON", "output.json", filepath])
                res = ogr2ogrCase("output.json")
                os.chdir(curDir)
            return res
        # errors
        except:
            return (None, "file not found or your gml/xml/kml data is not valid")

    def ogr2ogrCase(filepath):
        """Method for extracting the crs of a valid GeoJSON file\n
        @param filepath Full path to GeoJSON
        @returns a boundingbox as an array in a tuple in WGS84, formated like ([minLong, minLat, maxLong, maxLat], None)
        """
        try:
            myGeojson = pygeoj.load(filepath=filepath)
            crs = myGeojson.crs['properties']['name']
            if crs.find('EPSG') != -1:
                crs = int(crs.split(':')[-1])
            else:
                return (None, "No reference system found or not as EPSG Code")

            pointList = []
            for features in myGeojson:
                # the coordinates are beeing extracted from the GeoJSON and transformed into wgs84 coordinates
                pointList.extend(list(map(lambda point: CRSTransform(point[1], point[0], crs), list(
                    map(tuple, getCoordinatesFromGeoJson(features.geometry.coordinates))))))

            return (convex_hull(pointList), None)
        except:
            return (None, "File Error!")

#################################################################

    # shapefile handelig
    if file_extension == ".shp":
        return shapefileCase(filepath)

    # geojson handeling
    elif file_extension in (".json", ".geojson"):
        return jsonCase(filepath)

    # netCDF and GeoTiff handeling
    elif file_extension in (".tif", ".tiff", ".nc"):
        return ncTiffCase(name, path)

    # GeoPackage handeling
    elif file_extension == ".gpkg":
        return geoPackageCase(filepath)

    # csv or csv formated textfile handeling (csv on the web)
    elif file_extension in (".csv", ".txt"):
        return csvCase(filepath)

    # gml handeling
    elif file_extension in (".gml", ".xml", ".kml"):
        return ISOCase(filepath)

    # if the extension has not been implemented yet or won't be supported
    else:
        return (None, "type %s not yet supported" % file_extension)

#################################################################


def CRSTransform(Long, Lat, refsys):
    # Coordinate Reference System (CRS)
    SourceEPSG = refsys
    TargetEPSG = 4326

    source = osr.SpatialReference()
    source.ImportFromEPSG(SourceEPSG)

    target = osr.SpatialReference()
    target.ImportFromEPSG(TargetEPSG)

    transform = osr.CoordinateTransformation(source, target)
    point = ogr.CreateGeometryFromWkt("POINT (%s %s)" % (Long, Lat))
    point.Transform(transform)
    return (point.GetX(), point.GetY())


def convex_hull(points):
    """Computes the convex hull of a set of 2D points.

    Input: an iterable sequence of (x, y) pairs representing the points.
    Output: a list of vertices of the convex hull in counter-clockwise order,
      starting from the vertex with the lexicographically smallest coordinates.
    Implements Andrew's monotone chain algorithm. O(n log n) complexity.
    @see https://en.wikibooks.org/wiki/Algorithm_Implementation/Geometry/Convex_hull/Monotone_chain
    """

    # Sort the points lexicographically (tuples are compared lexicographically).
    # Remove duplicates to detect the case we have just one unique point.
    points = sorted(set(points))

    # Boring case: no points or a single point, possibly repeated multiple times.
    if len(points) <= 1:
        return points

    # 2D cross product of OA and OB vectors, i.e. z-component of their 3D cross product.
    # Returns a positive value, if OAB makes a counter-clockwise turn,
    # negative for clockwise turn, and zero if the points are collinear.
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    # Build lower hull
    lower = []
    for p in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    # Build upper hull
    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    # Concatenation of the lower and upper hulls gives the convex hull.
    # Last point of each list is omitted because it is repeated at the beginning of the other list.
    return lower[:-1] + upper[:-1]


def getCoordinatesFromGeoJson(listInList):
    coordinates = []
    for sublist in listInList:
        if type(sublist) is list:
            if type(sublist[0]) is list:
                coordinates.extend(getCoordinatesFromGeoJson(sublist))
            else:
                coordinates.extend(listInList)
                break
        else:
            coordinates.append(listInList)
            break
    return coordinates


# Main method
if __name__ == '__main__':
    main()
