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
@click.option('--folder', type=click.Choice(['single', 'whole']), default='single', help='select if you want to get the Metadata from the whole folder or for each seperate file.')

def click_function(path, detail, folder, time):
    getMetadata(path, detail, folder, time)

"""
Function for extracting the metadata (bounding box)
An advantage of our code is that the file extension is not important for the metadataextraction but the content of the file

:param path: path to the directory of the files or to the file itself
:param detail: specifies the level of detail of the geospatial extent (bbox or convex hull)
:param folder: specifies if the user gets the metadata for the whole folder "whole" or for each file "single"
:param time: boolean variable, if it is true the user gets the temporal extent instead of the spatial extent
:returns: spatial extent as a bbox in the format [minlon, minlat, maxlon, maxlat]
"""
def getMetadata(path, detail, folder, time):
   
    filepath = path
   
    if(len(filepath)==0):
        click.echo("Please insert a correct filepath")
        return None
    try:
        #click.echo("Shapefile")
        a=getShapefileInfo.getShapefilebbx(filepath, detail, folder, time)
    except Exception as e:
        try:
            #click.echo("GeoJson")
            a=getGeoJsonInfo.getGeoJsonbbx(filepath, detail, folder, time)
        except Exception as e:
            try:
                #click.echo("NetCDF")
                a=getNetCDFInfo.getNetCDFbbx(filepath, detail, folder, time)
            except Exception as e:
                try:
                    #print("CSV")
                    a=getCSVInfo.getCSVbbx(filepath, detail, folder, time)
                except Exception as e:
                    try:
                        #print("GeoPackage")
                        a=getGeoPackageInfo.getGeopackagebbx(filepath, detail, folder, time)
                    except Exception as e:
                        try:
                            #click.echo("GeoTIFF")
                            a=getGeoTiffInfo.getGeoTiffbbx(filepath, detail, folder, time)
                        except Exception as e:
                            try:
                                #click.echo("ISO")
                                a=getIsoInfo.getIsobbx(filepath, detail, folder, time)
                            except Exception as e:
                                try:
                                    #click.echo("Folder")
                                    a=openFolder.openFolder(filepath, detail, folder, time)
                                except Exception as e:
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
