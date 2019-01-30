import click                            # used to print something 
import shapefile                        # used to read the shapefile
import extractTool                      # used for the the transformation and prints  # used for the the transformation and prints
from scipy.spatial import ConvexHull    # used to calculate the convex hull

"""
Function for extracting the bounding box of a shapefile

:param filepath: path to the files
:param detail: specifies the level of detail of the geospatial extent (bbox or convex hull)
:param time: boolean variable, if it is true the user gets the temporal extent instead of the spatial extent
:returns: spatial extent as a bbox in the format [minlon, minlat, maxlon, maxlat]
"""
def getShapefilebbx(filepath, detail, time):    
    if detail =='bbox':
        bbox_val=shapefile_bbox(filepath)       
    else:
        bbox_val=[None]

    if detail == 'convexHull':
        convHull_val=shapefile_convexHull(filepath)
    else:
        convHull_val=[None]

    if (time):
        time_val=[None]
    else:
        time_val=[None]

    ret_value=[bbox_val, convHull_val, time_val]
    click.echo(ret_value)
    return ret_value

"""
Function for extracting the convex hull

:param filepath: path to the file
:returns: convex hull of the shapefile
"""
def shapefile_convexHull(filepath):
    sf = shapefile.Reader(filepath)
    shapes=sf.shapes()
    allPts=[]
    for z in shapes:
        points=z.points
        allPts=allPts+points
    hull=ConvexHull(allPts)
    hull_points=hull.vertices
    convHull=[]
    click.echo(hull_points)
    for y in hull_points:
        point=[allPts[y][0], allPts[y][1]]
        convHull.append(point)
    click.echo(point)
    click.echo("Missing CRS -----> Convex hull will not be saved in zenodo.")
    return [None]

"""
Function for extracting the temporal extent of a shapefile. But for now there is no time value for shapefiles. So it just returns None

:param filepath: path to the file
:returns: None
"""
def shapefile_time(filepath):
    click.echo="There is no timevalue for Shapefiles"
    return [None]

"""
Function for extracting the bbox using shapefile reader

:param filepath: path to the file
:returns: None, because we could not detect a crs
"""
def shapefile_bbox(filepath):
    #if the file is a valid shapefile it will be opened with this function.
    #otherwise an exception will be thrown.
    sf = shapefile.Reader(filepath)
    output = sf.bbox
    extractTool.print_pretty_bbox(filepath, output, "Shapefile")
    click.echo("Missing CRS -----> Boundingbox will not be saved in zenodo.")
    return [None]
    
if __name__ == '__main__':
    getShapefilebbx()
