'''
Created on 15.01.2018
@author: Henry Fock, Anika Graupner
'''

import click

from geodataExtent import extractGeoDataFromFolder as fext
from geodataExtent import getBoundingBox as box
from geodataExtent import getPolygon as poly
from geodataExtent import getTimeExtent as timeext


# asking for parameters in command line
@click.command()
@click.option('--path', prompt="Please enter path to Folder", help='Path to Folder containing Geofiles')
@click.option('--clear','-c', default=False, is_flag=True, help='Clear screen before showing results')
@click.option('--time', '-t', default=False, is_flag=True, help="execute time extraction for one file")
@click.option('--space', '-s', default=False, is_flag=True, help="execute boundingbox extraction for one file")
@click.option('--hull', '-h', default=False, is_flag=True, help="execute convex-hull extraction for one file")
def main(path, clear, time, space, hull):
    """Main CLI-Tool combining all the single extraction tools in one tool.

    \nNo return but Console-Output of the wanted extents. If time, space and hull are all false, the folder extraction will be triggered and returns a table with the boundingbox and spatial extent for each individual file in addition to the full time and spatial extent of he folder.\nIssue: If there are files that are not in WGS84 and do not have a specified referencesystem, the spatial extent of the folder will might not be in WGS84
    """
    output = []

    name = ""
    if time or space or hull:
        name = click.prompt("Please enter filename")

    def timeOption(path, name):
        res = timeext.getTimeExtent(name, path)
        if res[0] is not None:
            return res[0]
        else:
            return res[1]

    def spaceOption(path, name):
        res = box.getBoundingBox(name, path)
        if res[0] is not None:
            return res[0]
        else:
            return res[1]

    def polyOption(path, name):
        res = poly.getPolygon(name, path)
        if res[0] is not None:
            return res[0]
        else:
            return res[1]

#################################################################

    if time:
        output.append("Timeextent:")
        output.append(timeOption(path, name))
        output.append("\n")
    
    if space:
        output.append("Spatialextent:")
        output.append(spaceOption(path, name))
        output.append("\n")

    if hull:
        output.append("Spatialextent as Convex Hull:")
        output.append(polyOption(path, name))
        output.append("\n")

    if not (time or space or hull):
        fext.extractFromFolder(path, clear)
    else:
        if clear:
            click.clear()
        for x in output:
            click.echo(x)

if __name__ == "__main__":
    main()
