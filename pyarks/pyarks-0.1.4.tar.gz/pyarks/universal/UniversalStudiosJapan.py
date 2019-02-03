import json

import pkg_resources
import requests

import pyarks.utility
from pyarks.park import Park
from pyarks.ride import Ride


class UniversalStudiosJapan(Park):
    def __init__(self):
        self.rides = self.getRides()
        super(UniversalStudiosJapan, self).__init__("Universal Studios Japan")

    def getRides(self):
        rides = []
        response = self.getResponse()
        if response["status"] == 2:
            self.isOpen = False
            resource_package = __name__  # Could be any module/package name
            resource_path = '/'.join(('data', 'USJ.json'))  # Do not use os.path.join(), see below

            datafile = json.loads(pkg_resources.resource_string(resource_package, resource_path))

            for ride in datafile["List"][0]["Rows"]:
                rides.append(Ride(self, ride["Text"].encode("utf-8"), -1, ""))
            return rides
        else:
            self.isOpen = True
            #Fill in here when the park is open
            for waitTimeGroup in response["list"]:
                if utility.USJTranslate(waitTimeGroup["wait"].encode("utf-8")) == "Inactive":
                    waitTime = -2
                else:
                    waitTime = int(waitTimeGroup["wait"][:-1])
                for ride in waitTimeGroup["rows"]:
                    rides.append(Ride(self, utility.USJTranslate(ride["text"].encode("utf-8")), waitTime, ""))
            return rides

    def getResponse(self):
        return requests.get("http://ar02.biglobe.ne.jp/app/waittime/waittime.json").json()
