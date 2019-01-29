"""
creates a skymap in healpix representation with data from GAIA.


    This work has made use of data from the European Space Agency (ESA)
    mission {\\it Gaia} (\\url{https://www.cosmos.esa.int/gaia}), processed by
    the {\\it Gaia} Data Processing and Analysis Consortium (DPAC,
    \\url{https://www.cosmos.esa.int/web/gaia/dpac/consortium}). Funding
    for the DPAC has been provided by national institutions, in particular
    the institutions participating in the {\\it Gaia} Multilateral Agreement..


This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>

Created and maintained by Matthias Buechele [FAU].

"""

import http.client
import urllib.parse
import time
from xml.dom.minidom import parseString


class query(object):
    """docstring for query"""
    def __init__(self, magmin, magmax):
        self.magmin = magmin
        self.magmax = magmax
        self.host = "gea.esac.esa.int"
        self.port = 80
        self.pathinfo = "/tap-server/tap/async"
        self.timestart = time.time()
        self.jobid = ''

    def submit(self):
        """
        Creates a ADQL query at gaia archive
        """

        params = urllib.parse.urlencode({
            "REQUEST": "doQuery",
            "LANG": "ADQL",
            "FORMAT": "csv",
            "PHASE": "RUN",
            "JOBNAME": "Any name (optional)",
            "JOBDESCRIPTION": "Any description (optional)",
            "QUERY": "SELECT source_id,ra,dec,phot_g_mean_flux,phot_g_mean_mag FROM gaiadr1.gaia_source WHERE phot_g_mean_mag >= " +
            str(self.magmin) + " and phot_g_mean_mag<= " + str(self.magmax)})

        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "Accept": "text/plain"}

        print('GAIA: We submitted a query to ESA asking for all stars with Magnitude in range [%.2f, %.2f]' % (self.magmin, self.magmax))

        connection = http.client.HTTPConnection(self.host, self.port)
        connection.request("POST", self.pathinfo, params, headers)

        # Status
        response = connection.getresponse()
        print("GAIA: Status: " + str(response.status), "Reason: " + str(response.reason))

        # Server job location (URL)
        location = response.getheader("location")
        print("GAIA: Location: " + location)

        # Jobid
        self.jobid = location[location.rfind('/') + 1:]
        print("GAIA: Job id: " + self.jobid)

        timestart = time.time()
        print("GAIA: Started at %s" % time.strftime("%H:%M:%S", time.localtime(timestart)))

        connection.close()

    def checkStatus(self):
        """
        Check job status, wait until finished
        """
        sleep = 0.25
        while True:
            connection = http.client.HTTPConnection(self.host, self.port)
            connection.request("GET", self.pathinfo + "/" + self.jobid)
            response = connection.getresponse()
            data = response.read()
            # XML response: parse it to obtain the current status
            dom = parseString(data)
            phaseElement = dom.getElementsByTagName('uws:phase')[0]
            phaseValueElement = phaseElement.firstChild
            phase = phaseValueElement.toxml()
            # Check finished
            if phase == 'COMPLETED':
                print("GAIA: Status: %s\t --> finished after %i seconds" % (phase, time.time() - self.timestart))
                break
            print("GAIA: Status: %s\t since %i seconds" % (phase, time.time() - self.timestart))
            # wait and repeat
            time.sleep(sleep)
            if sleep < 10:
                sleep *= 2
        connection.close()

    def getResult(self):
        print('GAIA: Now downloading the results...')
        time2 = time.time()
        connection = http.client.HTTPConnection(self.host, self.port)
        connection.request("GET", self.pathinfo + "/" + self.jobid + "/results/result")
        response = connection.getresponse()
        data = response.read().decode().split('\n')
        print('GAIA: Downloaded %i lines of data in %.1f seconds' % (len(data) - 2, time.time() - time2))
        connection.close()
        return data[1:-1]

