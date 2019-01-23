'''
Created on 15.01.2018
@author: Henry Fock, Anika Graupner
'''

import click
import time as timeModule
import requests
import os

from geodataExtent import getBoundingBox as box
from geodataExtent import getTimeExtent as timeext


# asking for parameters in command line
@click.command()
@click.option('--path', prompt="Please enter path to Folder", help='Path to Folder containing Geofiles')
@click.option('--name', prompt="File name", help="Filename with extension")
@click.option('--id', '-i', 'ident', prompt="Please enter correct file ID for PyCSW", help="PyCSW ID of corrosponding file")
def main(path, name, ident):
    """CLI-Tool for extracting the spatial and temporal extant of a selected Geodile and sends the results to the corrosponding ID in PyCSW to update the entery. 

    \nReturns the XML Response of PyCSW after the update in the consloe
    """

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

    def builtXML(spatialExtentAsWKT, timeExtentStart, timeExtentEnd, ID, fileFormat):
        updatexml = """<?xml version="1.0" encoding="UTF-8"?>
<csw:Transaction xmlns:ogc="http://www.opengis.net/ogc" xmlns:csw="http://www.opengis.net/cat/csw/2.0.2" xmlns:ows="http://www.opengis.net/ows" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/cat/csw/2.0.2 http://schemas.opengis.net/csw/2.0.2/CSW-publication.xsd" service="CSW" version="2.0.2">
  <csw:Update>
	<csw:RecordProperty>
      <csw:Name>apiso:Modified</csw:Name>
      <csw:Value>%(actual_date)s</csw:Value>
    </csw:RecordProperty>
    <csw:RecordProperty>
      <csw:Name>apiso:BoundingBox</csw:Name>
      <csw:Value>%(bbox)s</csw:Value>
    </csw:RecordProperty>
	<csw:RecordProperty>
      <csw:Name>apiso:TempExtent_begin</csw:Name>
      <csw:Value>%(date_begin)s</csw:Value>
    </csw:RecordProperty>
	<csw:RecordProperty>
      <csw:Name>apiso:TempExtent_end</csw:Name>
      <csw:Value>%(date_end)s</csw:Value>
    </csw:RecordProperty>
	<csw:RecordProperty>
      <csw:Name>apiso:Format</csw:Name>
      <csw:Value>%(file_format)s</csw:Value>
    </csw:RecordProperty>
    <csw:Constraint version="1.1.0">
      <ogc:Filter>
        <ogc:PropertyIsEqualTo>
          <ogc:PropertyName>apiso:Identifier</ogc:PropertyName>
          <ogc:Literal>%(id)s</ogc:Literal>
        </ogc:PropertyIsEqualTo>
      </ogc:Filter>
    </csw:Constraint>
  </csw:Update>
</csw:Transaction>
"""
        date = timeModule.strftime("%Y-%m-%d")
        data = {'actual_date':date , 'bbox':spatialExtentAsWKT, 'date_begin':timeExtentStart, 'date_end':timeExtentEnd, 'file_format':fileFormat, 'id':ID}
        xml = updatexml%data

        return xml


#################################################################

    if ident is None:
        click.echo("ID is not valid", err=True)
        return None

    spatialExtent = ""
    start, end = "", ""
    filename, file_extension = os.path.splitext(name)

    space = spaceOption(path, name)
    time = timeOption(path, name)

    if type(space) is list:
        spatialExtent = 'POLYGON((%(minx)s %(miny)s, %(minx)s %(maxy)s, %(maxx)s %(maxy)s, %(maxx)s %(miny)s, %(minx)s %(miny)s))'
        boxData = {'minx': space[0], 'miny': space[1],
                   'maxx': space[2], 'maxy': space[3]}
        spatialExtent = spatialExtent % boxData
    else:
        click.echo(space, err=True)

    if type(time) is list:
        start, end = time[:2]
    else:
        click.echo(time, err=True)

    

    xml = builtXML(spatialExtent, start, end, ident, file_extension)
    r = requests.post('http://localhost:8000/csw', data=xml)
    click.echo(r.content)


if __name__ == "__main__":
    main()
