'''
Created on 29.10.2018
@author: Henry Fock, Lia Kirsch
'''

import csv
import os
import sys
import sqlite3
import tempfile

# add local modules folder
# file_path = os.path.join('..', 'Python_Modules')
# sys.path.append(file_path)

from osgeo import gdal, ogr, osr
import click
# import netCDF4 as nc
import pandas as pd
import pygeoj
import shapefile
import xarray as xr
import ogr2ogr

# asking for parameters in command line


@@click.command()
@click.option('--path', prompt="File path", help='Path to file')
@click.option('--name', prompt="File name", help="Filename with extension")
@click.option('--clear', '-c', default=False, is_flag=True, help='Clear screen before showing results')
def main(path, name, clear):
    res = getBoundingBox(name, path)
    if clear:
        click.clear()
    if res[0] is not None:
        click.echo(res[0])
    else:
        click.echo(res[1])


def getBoundingBox(name, path):
    """returns the bounding Box of supported Datatypes and standards in WGS84. The file MUST contain a valid CRS or has to be standardized like GeoJSON is WGS84\n
    supported data: Shapefile (.shp), GeoJson (.json/.geojson), GeoTIFF (.tif), netCDF (.nc), GeoPackage (.gpkg), all ISO19xxx standardised formats and CSV on the web\n
    @param path Path to the file
    @param name name of the file with extension
    @returns a boundingbox as an array in a tuple in WGS84, formated like ([minLong, minLat, maxLong, maxLat], None)
    """
    # connect name and path to file
    filepath = os.path.join(path, name)
    if not os.path.exists(filepath):
        return (None, "File not found!")
    # get file extension
    filename, file_extension = os.path.splitext(filepath)

#################################################################
    def shapefileCase(filepath):
        """Method for extracting the boundingbox of a shapefile\n
        @param filepath Full path to shapefile
        @returns a boundingbox as an array in a tuple in WGS84, formated like ([minLong, minLat, maxLong, maxLat], None)
        """
        try:
            dataset = ogr.Open(filepath)
            layer = dataset.GetLayer()
            crs = layer.GetSpatialRef()
            if crs is None:
                return (None, "CRS does not exist!")
            if crs.IsProjected() == 1:
                crs = int(crs.GetAttrValue("PROJCS|AUTHORITY", 1))
            elif crs.IsGeographic() == 1:
                crs = int(crs.GetAttrValue("GEOGCS|AUTHORITY", 1))
            else:
                return (None, "CRS is missing!")

            myshp = open(filepath, "rb")
            sf = shapefile.Reader(shp=myshp)
            envelope = sf.bbox
            bbox = CRSTransform(envelope[1], envelope[0], crs)
            bbox.extend(CRSTransform(envelope[3], envelope[2], crs))
        # error
        except:
            return (None, "File Error!")
        else:  # if no error accured
            return (bbox, None)

    def geojsonCase(filepath):
        """Method for extracting the boundingbox of a valid GeoJSON file\n
        @param filepath Full path to GeoJSON
        @returns a boundingbox as an array in a tuple in WGS84, formated like ([minLong, minLat, maxLong, maxLat], None)
        """
        try:
            myGeojson = pygeoj.load(filepath=filepath)
            return (myGeojson.bbox, None)
        except:
            return (None, "File Error!")

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
            bbox = myGeojson.bbox
            wgsBbox = CRSTransform(bbox[1], bbox[0], crs)
            wgsBbox.extend(CRSTransform(bbox[3], bbox[2], crs))
            return (wgsBbox, None)
        except:
            return (None, "File Error!")

    def tiffCase(filepath):
        """Method for extracting the boundingbox of a GeoTIFF\n
        @param filepath Full path to GeoTIFF
        @returns a boundingbox as an array in a tuple in WGS84, formated like ([minLong, minLat, maxLong, maxLat], None)
        """
        # @see https://stackoverflow.com/questions/2922532/obtain-latitude-and-longitude-from-a-geotiff-file
        try:
            # get the existing coordinate system
            ds = gdal.Open(filepath)
            old_cs = osr.SpatialReference()
            old_cs.ImportFromWkt(ds.GetProjectionRef())

            # create the new coordinate system
            wgs84_wkt = """
            GEOGCS["WGS 84",
                DATUM["WGS_1984",
                    SPHEROID["WGS 84",6378137,298.257223563,
                        AUTHORITY["EPSG","7030"]],
                    AUTHORITY["EPSG","6326"]],
                PRIMEM["Greenwich",0,
                    AUTHORITY["EPSG","8901"]],
                UNIT["degree",0.01745329251994328,
                    AUTHORITY["EPSG","9122"]],
                AUTHORITY["EPSG","4326"]]"""
            new_cs = osr.SpatialReference()
            new_cs .ImportFromWkt(wgs84_wkt)

            # create a transform object to convert between coordinate systems
            transform = osr.CoordinateTransformation(old_cs, new_cs)

            # get the point to transform, pixel (0,0) in this case
            width = ds.RasterXSize
            height = ds.RasterYSize
            gt = ds.GetGeoTransform()
            minx = gt[0]
            miny = gt[3] + width*gt[4] + height*gt[5]
            maxx = gt[0] + width*gt[1] + height*gt[2]
            maxy = gt[3]

            # get the coordinates in lat long
            latlongmin = transform.TransformPoint(minx, miny)
            latlongmax = transform.TransformPoint(maxx, maxy)
            bbox = [latlongmin[0], latlongmin[1], latlongmax[0], latlongmax[1]]
            return (bbox, None)
        # errors
        except:
            return (None, "File Error or TIFF is not GeoTIFF")

    def netCDFCase(filepath):
        """Method for extracting the boundingbox of a netCDF file

        @param filepath Full path to netCDF file
        @returns a boundingbox as an array in a tuple in WGS84, formated like ([minLong, minLat, maxLong, maxLat], None)
        @see https://gis.stackexchange.com/questions/270165/gdal-to-acquire-netcdf-like-metadata-structure-in-python
        """
        try:
            ds = xr.open_dataset(filepath)

            # get Dimensions
            dimensions = list(ds.to_dict()['dims'].keys())
            lon, lat = getLonLatCrs(dimensions)[:-1]
            # transform coordinates section in a dictionary
            coordinates = ds.to_dict()['coords']
            # get the coordinates as a list
            lats = coordinates[lat]['data']
            longs = coordinates[lon]['data']

            # taking the smallest and highest coordinates from the lists
            bbox = [min(longs), min(lats), max(longs), max(lats)]
            return (bbox, None)
        # errors
        except KeyError:
            return (None, "coordinate names may be spelled wrong: should be 'latitude'/'longitude")
        except:
            return (None, "File Error!")

    def geopackageCase(filepath):
        """Method for extracting the boundingbox of a GeoPackage

        @param filepath Full path to GeoPackage
        @returns a boundingbox as an array in a tuple in WGS84, formated like ([minLong, minLat, maxLong, maxLat], None)
        @see https://stackoverflow.com/questions/35945437/python-gdal-projection-conversion-from-wgs84-to-nztm2000-is-not-correct
        """
        try:
            conn = sqlite3.connect(filepath)
            c = conn.cursor()
            c.execute("""   SELECT min(min_x), min(min_y), max(max_x), max(max_y), srs_id
                            FROM gpkg_contents
                            WHERE NOT srs_id = 4327 OR srs_id = 4328
                            GROUP BY srs_id
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

            wgs84bboxen = []
            for bbox in bboxes:
                box = CRSTransform(bbox[1], bbox[0], bbox[4])
                box.extend(CRSTransform(bbox[3], bbox[2], bbox[4]))
                wgs84bboxen.append(box)

            bbox = [wgs84bboxen[0][0], wgs84bboxen[0][1],
                    wgs84bboxen[0][2], wgs84bboxen[0][3]]
            for wgs84Box in wgs84bboxen:
                if wgs84Box[0] < bbox[0]:
                    bbox[0] = wgs84Box[0]
                if wgs84Box[1] < bbox[1]:
                    bbox[1] = wgs84Box[1]
                if wgs84Box[2] > bbox[2]:
                    bbox[2] = wgs84Box[2]
                if wgs84Box[3] > bbox[3]:
                    bbox[3] = wgs84Box[3]
            return(bbox, None)
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
        """Method for extracting the boundingbox of a "CSV on the Web" formated file
        columns holding the coordinates must be named either longitude/lon/lng/long, latitude/lat and the CRS column must be named either crs/srs/reference system/coordinate reference systems\n
        @param filepath Full path to CSV/text file
        @returns a boundingbox as an array in a tuple in WGS84, formated like ([minLong, minLat, maxLong, maxLat], None)
        @see https://stackoverflow.com/questions/16503560/read-specific-columns-from-a-csv-file-with-csv-module
        """
        try:  # finding the correct columns for latitude and longitude
            csvfile = open(filepath)
            head = csv.reader(csvfile, delimiter=' ', quotechar='|')
            # get the headline an convert, if possible, ';' to ','
            # and seperate each word devided by a ',' into an array
            header = next(head)[0].replace(";", ",").split(",")

            # searching for valid names for latitude and longitude

            lng, lat, crs = getLonLatCrs(header)

            # if there is no valid name or coordinates, an exception is thrown an cought with an errormassage
            if(lat is None or lng is None):
                raise ValueError(
                    "please rename latitude an longitude: latitude/lat, longitude/lon/lng")
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

        # taking the smallest and highest coordinates from the lists if no exceptions accured
        bbox = CRSTransform(min(latitudes), min(longitudes), srs[0])
        bbox.extend(CRSTransform(max(latitudes), max(longitudes), srs[0]))
        return (bbox, None)

    def ISOCase(filepath):
        """Method for extracting the boundingbox of an ISO19xxx standardized file

        @param filepath Full path to the ISO19xxx standardized file
        @returns a boundingbox as an array in a tuple in WGS84, formated like ([minLong, minLat, maxLong, maxLat], None)
        @see https://gis.stackexchange.com/questions/39080/using-ogr2ogr-to-convert-gml-to-shapefile-in-python
        """
        try:  # in case GDAL works
            ogr.UseExceptions()
            isofile = ogr.CreateGeometryFromGML(filepath)
            crs = isofile.GetSpatialRef()
            if crs.IsProjected() == 1:
                crs = int(crs.GetAttrValue("PROJCS|AUTHORITY", 1))
            elif crs.IsGeographic() == 1:
                crs = int(crs.GetAttrValue("GEOGCS|AUTHORITY", 1))
            else:
                return (None, "CRS is missing!")
            bbox = isofile.GetEnvelope()
            result = CRSTransform(bbox[1], bbox[0], crs)
            result.extend(CRSTransform(bbox[3], bbox[2], crs))
            ogr.DontUseExceptions()
            return (result, None)
        except:
            try:
                # convert the gml file to a GeoJSON file
                with tempfile.TemporaryDirectory() as tmpdirname:
                    curDir = os.getcwd()
                    os.chdir(tmpdirname)
                    ogr2ogr.main(
                        ["", "-f", "GeoJSON", "output.json", filepath])
                    # get boundingbox from generated GeoJSON file
                    result = ogr2ogrCase("output.json")
                    os.chdir(curDir)
                # delete generated GeoJSON file
                return result
            # errors
            except:
                return (None, "file not found or your gml/xml/kml data is not valid")


#################################################################

    # shapefile handelig
    if file_extension == ".shp":
        return shapefileCase(filepath)

    # geojson handeling
    elif file_extension in (".json", ".geojson"):
        return geojsonCase(filepath)

    # GeoTiff handeling
    elif file_extension in (".tif", ".tiff"):
        return tiffCase(filepath)

    # netCDF handeling
    elif file_extension == ".nc":
        return netCDFCase(filepath)

    # geoPackage handeling
    elif file_extension == ".gpkg":
        return geopackageCase(filepath)

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


def CRSTransform(Lat, Long, refsys):
    # Input refsys = EPSG
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
    return [point.GetX(), point.GetY()]


def getLonLatCrs(searchList):
    """get the correct names of the columns holding the coordinates
    @param header Header of the CSV
    @returns (lon, lat, crs) where lon, lat, crs are the column names
    """
    lng = None
    lat = None
    crs = None
    for t in searchList:
        if t.lower() in ("longitude", "lon", "long", "lng"):
            lng = t
        if t.lower() in ("latitude", "lat"):
            lat = t
        if t.lower() in ("crs", "srs", "coordinate reference systems", "reference systems", "spatial reference system"):
            crs = t
    return (lng, lat, crs)


# Main method
if __name__ == '__main__':
    main()
