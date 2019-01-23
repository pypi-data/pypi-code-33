"""
@Author Henry Fock
"""
import sys
import os
# add local modules folder
# file_path = os.path.join('..', 'Python_Modules')
# sys.path.append(file_path)

from geodataExtent import getBoundingBox as box
from geodataExtent import getTimeExtent as timeEx
import threading

from os import listdir
from os.path import isfile, join
from osgeo import ogr
import click
from DateTime import DateTime
from tabulate import tabulate


@click.command()
@click.option('--path', prompt="Path to folder", help='Path to your folder as String')
@click.option('--clear', default=False, help='Flag wether you want to display only the Output')
def main(path, clear):
    extractFromFolder(path, clear)


def extractFromFolder(path, clear):
    threads = []
    res = []
    onlyfiles = [f for f in listdir(path) if isfile(
        join(path, f)) and os.path.splitext(f)[1] not in (".dbf", ".prj", ".shx", ".cpg")]

    for name in onlyfiles:
        current = CliTools(path, name)
        threads.append(current)
        current.start()

    for thread in threads:
        thread.join()
        res.append(thread.result)

    if clear:
        click.clear()

    output = []
    click.secho("\nResult:", blink=True)
    for x in res:
        if x[1][0] is None:
            if x[2][0] is None:
                output.append([x[0], x[1][1], x[2][1]])
            else:
                output.append([x[0], x[1][1], x[2][0]])
        else:
            if x[2][0] is None:
                output.append([x[0], x[1][0], x[2][1]])
            else:
                output.append([x[0], x[1][0], x[2][0]])

    click.echo(tabulate(output, headers=[
               'Filename', 'Boundingbox (minX/Lon, minY/Lat, maxX, maxY) / Error', 'Timeextent (stard, end, Average-interval in days) / Error']))

    # Create a geometry collection
    geomcol = ogr.Geometry(ogr.wkbGeometryCollection)
    lowTime, maxTime = None, None

    for x in res:
        if x[1][1] is None:
            box = ogr.Geometry(ogr.wkbLineString)
            box.AddPoint(x[1][0][0], x[1][0][1])
            box.AddPoint(x[1][0][0], x[1][0][3])
            box.AddPoint(x[1][0][2], x[1][0][1])
            box.AddPoint(x[1][0][2], x[1][0][3])
            geomcol.AddGeometry(box)

        if x[2][1] is None:
            if lowTime is None or DateTime(x[2][0][0]) < lowTime:
                lowTime = DateTime(x[2][0][0])

            if maxTime is None or DateTime(x[2][0][1]) > maxTime:
                maxTime = DateTime(x[2][0][1])

    env = geomcol.GetEnvelope()
    click.echo("\n")
    click.echo(tabulate([[str((env[0], env[2], env[1], env[3])).strip('()'), str((str(lowTime), str(
        maxTime))).strip('()')]], headers=['Boundingbox of Folder', 'Timeextent of Folder (ISO8601)']))
    click.echo("\n")

    # click.echo("\nFull spatial Extent as Boundingbox: %s" % str((env[0], env[2], env[1], env[3])))
    # click.echo("Full time Extend as ISO8601: %s" % str((str(lowTime), str(maxTime))))
    # click.echo("\n")


class CliTools(threading.Thread):
    def __init__(self, path, name):
        threading.Thread.__init__(self)
        self.path = path
        self.name = name
        self.result = []

    def run(self):
        bbox = box.getBoundingBox(path=self.path, name=self.name)
        time = timeEx.getTimeExtent(path=self.path, name=self.name)
        self.result.extend([self.name, bbox, time])


if __name__ == '__main__':
    main()
