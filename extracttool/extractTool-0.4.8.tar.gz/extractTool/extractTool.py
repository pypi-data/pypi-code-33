from pyproj import Proj, transform # used for the CRS transformation
import click    # used for output messages
import getShapefileInfo, getGeoTiffInfo, getCSVInfo, getIsoInfo, getGeoJsonInfo, getNetCDFInfo, getGeoPackageInfo, openFolder

"""
Auxiliary function to bypass problems with the CLI tool when executed from anywhere else

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

def click_function(path, detail, time):
    getMetadata(path, detail, time)

"""
Function for extracting the metadata (bounding box)
An advantage of our code is that the file extension is not important for the metadataextraction but the content of the file

:param path: path to the directory of the files or to the file itself
:param detail: specifies the level of detail of the geospatial extent (bbox or convex hull)
:param folder: specifies if the user gets the metadata for the whole folder "whole" or for each file "single"
:param time: boolean variable, if it is true the user gets the temporal extent instead of the spatial extent
:returns: spatial extent as a bbox in the format [minlon, minlat, maxlon, maxlat]
"""
def getMetadata(path, detail, time):
   
    filepath = path
    a = None
   
    if(len(filepath)==0):
        click.echo("Please insert a correct filepath")
        return None
    try:
        a=getShapefileInfo.getShapefilebbx(filepath, detail, time)
    except Exception as e:
        try:
            a=getGeoJsonInfo.getGeoJsonbbx(filepath, detail, time)
        except Exception as e:
            try:
                a=getNetCDFInfo.getNetCDFbbx(filepath, detail, time)
            except Exception as e:
                try:
                    a=getCSVInfo.getCSVbbx(filepath, detail, time)
                except ValueError as err:
                    print(err.args)
                except TypeError as e:
                    print(e.args)
                    try:
                        a=getGeoPackageInfo.getGeopackagebbx(filepath, detail, time)
                    except Exception as e:
                        try:
                            a=getGeoTiffInfo.getGeoTiffbbx(filepath, detail, time)
                        except Exception as e:
                            try:
                                a=getIsoInfo.getIsobbx(filepath, detail, time)
                            except Exception as e:
                                try:
                                    a=openFolder.openFolder(filepath, detail, time)
                                except Exception as e:
                                    print("88888888")
                                    print(e)
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

def print_pretty_bbox(path, bbox, my_format):
    print("----------------------------------------------------------------")
    click.echo("Filepath:")
    click.echo(path)
    click.echo("Boundingbox of the "+my_format+" object:")
    click.echo(bbox)
    print("----------------------------------------------------------------")

def print_pretty_hull(path, convHull, my_format):
    print("----------------------------------------------------------------")
    click.echo("Filepath:")
    click.echo(path)
    click.echo("Convex Hull of the "+my_format+" file: ")
    click.echo(convHull)
    print("----------------------------------------------------------------")

def print_pretty_time(path, time, my_format):
    print("----------------------------------------------------------------")
    click.echo("Timeextend of the "+my_format+" file:")
    click.echo(time)
    print("----------------------------------------------------------------")

if __name__ == '__main__':
    click_function()
