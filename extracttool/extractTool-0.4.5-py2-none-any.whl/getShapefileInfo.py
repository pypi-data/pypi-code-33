import click
import shapefile
import extractTool
from scipy.spatial import ConvexHull

"""
Function for extracting the bounding box of a shapefile

:param filepath: path to the files
:param detail: specifies the level of detail of the geospatial extent (bbox or convex hull)
:param folder: specifies if the user gets the metadata for the whole folder (whole) or for each file (single)
:param time: boolean variable, if it is true the user gets the temporal extent instead of the spatial extent
:returns: spatial extent as a bbox in the format [minlon, minlat, maxlon, maxlat]
"""
def getShapefilebbx(filepath, detail, folder, time):    
    #if the file is a valid shapefile it will be opened with this function.
    #otherwise an exception will be thrown.
    

    if detail =='bbox':
        bbox_val=shapefile_bbox(filepath, folder)       
    else:
        bbox_val=[None]
    if detail == 'convexHull':
        convHull_val=shapefile_convexHull(filepath, folder)
    else:
        convHull_val=[None]
    if (time):
        try: 
            time_val=shapefile_time(filepath, folder)
        except Exception as e:
            print(e)
        # print("+++++++++++++++++++++++++++")
        # print(time_val)
    else:
        time_val=[None]

    # if folder=='single':
    ret_value=[bbox_val, convHull_val, time_val]
    print(ret_value)
    return ret_value

def shapefile_convexHull(filepath, folder):
    sf = shapefile.Reader(filepath)
    shapes=sf.shapes()
    allPts=[]
    for z in shapes:
        points=z.points
        allPts=allPts+points
    hull=ConvexHull(allPts)
    hull_points=hull.vertices
    convHull=[]
    print(hull_points)
    for y in hull_points:
        point=[allPts[y][0], allPts[y][1]]
        convHull.append(point)
    print("#############################")
    print(point)
    print("#############################")
    #if folder =='single':
    # print("----------------------------------------------------------------")
    # click.echo("Filepath:")
    # click.echo(filepath)
    # click.echo("The convex hull of the Shapefile is:")    
    # click.echo(convHull)
    print("Missing CRS -----> Convex hull will not be saved in zenodo.")
    # print("----------------------------------------------------------------")
    return [None]
    #if folder=='whole':
    #    print("----------------------------------------------------------------")
    #    click.echo("Filepath:")
    #    click.echo(filepath)
    #    click.echo("The convex hull of the Shapefile is:")    
    #    click.echo(convHull)
    #    click.echo("Shapefiles cannot be used for the calculation of the folder because of the missing crs.")
    #    print("----------------------------------------------------------------")
        #TODO
        #extractTool.bboxArray=extractTool.bboxArray+convHull
        #click.echo(extractTool.bboxArray)


def shapefile_time(filepath, folder):
    click.echo="There is no timevalue for Shapefiles"
    timeval=[None]
    return timeval

def shapefile_bbox(filepath, folder):
    sf = shapefile.Reader(filepath)
    output = sf.bbox
    # if folder=='single':
    extractTool.print_pretty_bbox(filepath, output, "Shapefile")
    click.echo("Missing CRS -----> Boundingbox will not be saved in zenodo.")
    return [None]
    #if folder=='whole':
    #    print("----------------------------------------------------------------")
    #    click.echo("Filepath:")
    #    click.echo(filepath)
    #    click.echo("Boundingbox of the Shapefile:")
    #    click.echo(output)
    #    click.echo("Shapefiles cannot be used for the calculation of the whole folder because of the missing crs.")
    #    print("----------------------------------------------------------------")
    #    #TODO
    #    #adds the boundingbox of the shapefile to the bboxArray
    #    #extractTool.bboxArray.append(output)
    
if __name__ == '__main__':
    getShapefilebbx()
