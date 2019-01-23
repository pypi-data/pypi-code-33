###############################################################################
# (c) Copyright 2016 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''
Command line client that interfaces to the Installer class

:author: Stefan-Gabriel CHITIC
'''
from cernservicexml import ServiceDocument, Status, XSLSPublisher


class MonitoringGW(object):

    contact = 'lhcb-geoc@cern.ch'

    def __init__(self, serviceID, logger=None):
        self.serviceID = serviceID
        self.logger = logger
        self.doc = ServiceDocument(self.serviceID, status=Status.available,
                                   contact=self.contact)

    def sendMetrics(self, data):
        self.addMetrics(data)
        self.sendData()

    def addMetrics(self, data):
        for element in data:
            if not element.get('name', None) or not element.get('value', None):
                continue
            self.addMetric(element['name'],
                           int(element['value']),
                           description=element.get('description', None))

    def addMetric(self, name, value, description=None):
        self.doc.add_numericvalue(name, value, desc=description)

    def generateXml(self):
        return self.doc.to_xml()

    def sendData(self):
        response = XSLSPublisher.send(self.doc)
        if not response.status_code == 200:
            if self.logger:
                self.logger.write(
                    'Stats sending failed because:\n %s' % response.content,
                    0, "SERVER-INFO")
            else:
                print response.content
