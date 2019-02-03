from __future__ import print_function

import hmac
import json
import re
from base64 import b64encode
from datetime import datetime
from hashlib import sha256
from datetime import datetime

import requests
import arrow

import pyarks.utility as utility
from pyarks.park import Park
from pyarks.ride import Ride

requests.packages.urllib3.disable_warnings()


class UniversalUSPark(Park):
    baseURL = "https://services.universalorlando.com/api"

    def __init__(self, name):
        self.parkID = utility.universalNameToID(name)
        self.rides = self.getRides()
        self.isOpen = True
        self.schedule = self.getOpenCloseTime()
        super(UniversalUSPark, self).__init__(name)

    def getOpenCloseTime(self):
        return self.getReponseJSON("openingTime")

    def getRides(self):
        response = self.getReponseJSON("waitTime")
        rides = []
        for item in response:
            if item["VenueId"] == self.parkID:
                rides.append(Ride(self, item["MblDisplayName"].replace("™", "").replace("℠", ""), item["WaitTime"], item["MblLongDescription"]))

        return rides

    def getReponseJSON(self, dataType):
        SHARED_HEADERS = {
            "Accept": "application/json",
            "Accept-Language": "en-US",
            "X-UNIWebService-AppVersion": "1.2.1",
            "X-UNIWebService-Platform": "Android",
            "X-UNIWebService-PlatformVersion": "4.4.2",
            "X-UNIWebService-Device": "samsung SM-N9005",
            "X-UNIWebService-ServiceVersion": "1",
            "User-Agent": "Dalvik/1.6.0 (Linux; U; Android 4.4.2; SM-N9005 Build/KOT49H)",
            "Connection": "keep-alive",
            "Accept-Encoding": "gzip"
        }

        androidKey = "AndroidMobileApp"
        androidSecret = b"AndroidMobileAppSecretKey182014"

        date = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
        combinedKey = str.encode(androidKey + "\n" + date + "\n")
        sig = b64encode(
            hmac.new(androidSecret, combinedKey, sha256).digest()).strip()
        sig = re.sub("/\=$/", "\u003d", sig.decode('utf-8'))

        parameters = {
            "apiKey": androidKey,
            "signature": sig
        }

        headers = {
            "Date": date,
            "Content-Type": "application/json; charset=UTF-8"
        }

        headers.update(SHARED_HEADERS)

        r = requests.post("https://services.universalorlando.com/api", headers=headers,
                          data=json.dumps(parameters, ensure_ascii=False), verify=False)

        headers = {
            "X-UNIWebService-ApiKey": "AndroidMobileApp",
            "X-UNIWebService-Token": r.json()["Token"]
        }

        headers.update(SHARED_HEADERS)
        if dataType == "openingTime":
            now = arrow.now().shift(months=3)
            r = requests.get(self.baseURL + "/venues/" +
                             str(self.parkID) + "/hours?endDate=" + now.format('MM') + "/" +  now.format('DD') + "/" + now.format('YYYY'), headers=headers)
            response = r.json()
            days = []
            for day in response:
                days.append({'openTime': arrow.get(day["OpenTimeUnix"]), 'closeTime': arrow.get(day["CloseTimeUnix"]), 'earlyEntryTime': arrow.get(day["EarlyEntryUnix"])})
                
            return days

        if dataType == "waitTime":
            r = requests.get(
                self.baseURL + "/pointsofinterest/rides?pageSize=all", headers=headers)
            return r.json()["Results"]

        return results
