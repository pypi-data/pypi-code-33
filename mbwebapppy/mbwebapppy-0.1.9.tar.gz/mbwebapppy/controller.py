# -*- coding: utf-8 -*-
""" Simple Mercedes me API.

Attributes:
    username (int): mercedes me username (email)
    password (string): mercedes me password
    update_interval (int): min update intervall in seconds

"""

import json
import logging
import time
from multiprocessing import RLock
import requests
import lxml.html
# from mbwebapppy import Exceptions as mbmeExc

_LOGGER = logging.getLogger(__name__)

SERVER_UI = "https://ui.meapp.secure.mercedes-benz.com"
SERVER_LOGIN = "https://login.secure.mercedes-benz.com"
SERVER_APP = "https://app.secure.mercedes-benz.com"
SERVER_API = "https://api.secure.mercedes-benz.com"

API_VEHICLES = "backend/vehicles"
ME_STATUS_URL = "{0}/backend/users/identity".format(SERVER_APP)
CAR_STATUS_URL = "{0}/backend/vehicles/%s/status".format(SERVER_APP)
CAR_DETAIL_URL = "{0}/backend/vehicles/%s/converant".format(SERVER_APP)
LOGIN_STEP1_URL = "{0}/session/login?app-id=VHPMBCON.PRODEC".format(SERVER_APP)
LOGIN_STEP2_URL = "/wl/login"
LOGIN_STEP3_URL = "{0}/oidc10/auth/oauth/v2/authorize/consent".format(SERVER_API)

CONTENT_TYPE_JSON = "application/json;charset=UTF-8"


ODOMETER_OPTIONS = ["odo",
                    "distanceReset",
                    "distanceStart",]

LOCATION_OPTIONS = ["positionLat",
                    "positionLong",
                    "positionHeading"]

TIRE_OPTIONS = ["tirepressureRearLeft",
                "tirepressureRearRight",
                "tirepressureFrontRight",
                "tirepressureFrontLeft"]

WINDOW_OPTIONS = ["windowstatusrearleft",
                  "windowstatusrearright",
                  "windowstatusfrontright",
                  "windowstatusfrontleft"]

DOOR_OPTIONS = ["doorstatusrearleft",
                "doorstatusrearright",
                "doorstatusfrontright",
                "doorstatusfrontleft",
                "doorlockstatusrearleft",
                "doorlockstatusrearright",
                "doorlockstatusfrontright",
                "doorlockstatusfrontleft",
                "doorlockstatusdecklid",
                "doorlockstatusvehicle",
                "doorlockstatusgas"]

ELECTRIC_OPTIONS = ["distanceElectricalStart",
                    "electricalRangeSkipIndication",
                    "electricconsumptionstart",
                    "electricconsumptionreset",
                    "distanceElectricalReset"]

BINARY_SENSOR_OPTIONS = ["warningwashwater",
                         "decklidstatus",
                         "warningenginelight",
                         "warningbrakefluid",
                         "parkbrakestatus"]

DEBUG_MODE = False

# Set to False for testing with tools like fiddler
# Change to True for production
LOGIN_VERIFY_SSL_CERT = True


class Car(object):
    def __init__(self):
        self.licenseplate = None
        self.finorvin = None
        self.salesdesignation = None
        self.nickname = None
        self.modelyear = None
        self.colorname = None
        self.fueltype = None
        self.powerhp = None
        self.powerkw = None
        self.numberofdoors = None
        self.numberofseats = None
        self.binarysensors = None
        self.tanklevelpercent = None
        self.liquidconsumptionstart = None
        self.liquidconsumptionreset = None
        self.rangeliquid = None
        self.tires = None
        self.odometer = None
        self.fuellevelpercent = None
        self.doors = None
        self.stateofcharge = None
        self.location = None
        self.windows = None
        self.doors = None

class StateOfObject(object):
    def __init__(self, unit=None, value=None, retrievalstatus=None, timestamp=None):
        self.unit = None
        self.value = None
        self.retrievalstatus = None
        self.timestamp = None
        if unit is not None:
            self.unit = unit
        if value is not None:
            self.value = value
        if retrievalstatus is not None:
            self.retrievalstatus = retrievalstatus
        if timestamp is not None:
            self.timestamp = timestamp

class Odometer(object):
    def __init__(self):
        self.odo = None
        self.distanceReset = None
        self.distanceStart = None

class Tires(object):
    def __init__(self):
        self.tirepressurefrontleft = None
        self.tirepressurefrontright = None
        self.tirepressurerearleft = None
        self.tirepressurerearright = None

class Windows(object):
    def __init__(self):
        self.windowstatusfrontleft = None
        self.windowstatusfrontright = None
        self.windowstatusrearleft = None
        self.windowstatusrearright = None

class Doors(object):
    def __init__(self):
        self.doorstatusfrontleft = None
        self.doorstatusfrontright = None
        self.doorstatusrearleft = None
        self.doorstatusrearright = None
        self.doorlockstatusfrontleft = None
        self.doorlockstatusfrontright = None
        self.doorlockstatusrearleft = None
        self.doorlockstatusrearright = None
        self.doorlockstatusdecklid = None
        self.doorlockstatusgas = None
        self.doorlockstatusvehicle = None

class Electric(object):
    def __init__(self):
        self.distanceelectricalstart = None
        self.electricalrangeskipindication = None
        self.electricconcumptionstart = None
        self.electricconsumptionreset = None
        self.distanceelectricalreset = None

class Binary_Sensors(object):
    def __init__(self):
        self.warningwashwater = None
        self.decklidstatus = None
        self.warningenginelight = None
        self.warningbrakefluid = None
        self.parkbrakestatus = None

class Location(object):
    def __init__(self, latitude=None, longitude=None, heading=None):
        self.latitude = None
        self.longitude = None
        self.heading = None
        if latitude is not None:
            self.latitude = latitude
        if longitude is not None:
            self.longitude = longitude
        if heading is not None:
            self.heading = heading

class CarAttribute(object):
    def __init__(self, value, retrievalstatus, timestamp):
        self.value = value
        self.retrievalstatus = retrievalstatus
        self.timestamp = timestamp

class Controller(object):
    """ Simple Mercedes me API.
    """
    def __init__(self, username, password, update_interval):

        self.__lock = RLock()
        self.cars = []
        self.update_interval = update_interval
        self.is_valid_session = False
        self.last_update_time = 0
        self.username = username
        self.password = password
        self.session = requests.session()
        self.session_cookies = self._get_session_cookies(username, password)
        self.session_refreshing = False
        if self.is_valid_session:
            self._get_cars()


    def update(self):
        """ Simple Mercedes me API."""
        _LOGGER.info("Update start")
        self._update_cars()

    def _update_cars(self):
        cur_time = time.time()
        with self.__lock:
            if cur_time - self.last_update_time > self.update_interval:
                for car in self.cars:
                    # session_check
                    self._retrieve_api_result(car.finorvin, "status")

                    api_result = self._retrieve_api_result(
                        car.finorvin,
                        "status").get("data")
                    car.binarysensors = self._get_binary_sensors(
                        api_result, car.finorvin)

                    car.tanklevelpercent = self._get_car_attribute(
                        api_result,
                        "tanklevelpercent")
                    car.liquidconsumptionstart = self._get_car_attribute(
                        api_result,
                        "liquidconsumptionstart")
                    car.liquidconsumptionreset = self._get_car_attribute(
                        api_result,
                        "liquidconsumptionreset")
                    car.rangeliquid = self._get_car_attribute(
                        api_result,
                        "rangeliquid")

                    car.odometer = self.get_odometer(api_result, car.finorvin)
                    car.tires = self.get_tires(api_result, car.finorvin)
                    car.windows = self.get_windows(api_result, car.finorvin)
                    car.doors = self.get_doors(api_result, car.finorvin)
                    car.location = self.get_location(car.finorvin)
                    car.electric = self.get_electric(api_result, car.finorvin)

                self.last_update_time = time.time()

    def _get_cars(self):
        cur_time = time.time()
        with self.__lock:
            if cur_time - self.last_update_time > self.update_interval:
                response = self.session.get(ME_STATUS_URL,
                                            verify=LOGIN_VERIFY_SSL_CERT)

                #if response.headers["Content-Type"] == CONTENT_TYPE_JSON:
                cars = json.loads(
                    response.content.decode('utf8'))['vehicles']

                for c in cars:
                    car = Car()
                    car.finorvin = c.get("vin")
                    car.licenseplate = c.get("licenceplate")
                    response = self.session.get(CAR_DETAIL_URL % car.finorvin,
                                                verify=LOGIN_VERIFY_SSL_CERT)

                    _LOGGER.debug(response.text)

                    detail = json.loads(response.content.decode('utf8'))

                    car.salesdesignation = detail.get("salesDesignation")

                    api_result = self._retrieve_api_result(car.finorvin, "status").get("data")
                    car.binarysensors = self._get_binary_sensors(api_result, car.finorvin)
                    car.tanklevelpercent = self._get_car_attribute(api_result, "tanklevelpercent")
                    car.liquidconsumptionstart = self._get_car_attribute(
                        api_result,
                        "liquidconsumptionstart")
                    car.liquidconsumptionreset = self._get_car_attribute(
                        api_result,
                        "liquidconsumptionreset")
                    car.rangeliquid = self._get_car_attribute(
                        api_result,
                        "rangeliquid")
                    car.odometer = self.get_odometer(api_result, car.finorvin)
                    car.tires = self.get_tires(api_result, car.finorvin)
                    car.windows = self.get_windows(api_result, car.finorvin)
                    car.doors = self.get_doors(api_result, car.finorvin)
                    car.location = self.get_location(car.finorvin)

                    self.cars.append(car)

                self.last_update_time = time.time()

    def _get_car_attribute(self, c, attribute_name):
        _LOGGER.debug("get_car_attribute %s for %s called",
                      attribute_name, 
                      c.get("vin"))

        option_status = CarAttribute(c.get(attribute_name).get("value"),
                                     c.get(attribute_name).get("status"),
                                     c.get(attribute_name).get("ts"))
        return option_status

    def _get_binary_sensors(self, car_detail, car_id):
        _LOGGER.debug("_get_binary_sensors for %s called", car_id)        

        binary_sensors = Binary_Sensors()

        for binary_sensor_option in BINARY_SENSOR_OPTIONS:
            option = car_detail.get(binary_sensor_option)
            option_status = CarAttribute(option.get("value"),
                                             option.get("status"),
                                             option.get("ts"))
            setattr(binary_sensors, binary_sensor_option, option_status)
        
        return binary_sensors

    def get_odometer(self, car_detail, car_id):
        _LOGGER.debug("get_odometer for %s called", car_id)

        odometer = Odometer()

        for odometer_option in ODOMETER_OPTIONS:
            if car_detail is not None:
                option = car_detail.get(odometer_option)
                option_status = CarAttribute(option.get("value"),
                                             option.get("status"),
                                             option.get("ts"))
                setattr(odometer, odometer_option, option_status)
            else:
                _LOGGER.warning("get_odometer for %s failed", car_id)        
                setattr(odometer, odometer_option, CarAttribute(-1, -1, None))

        return odometer

    def get_windows(self, car_detail, car_id):
        _LOGGER.debug("get_windows for %s called", car_id)

        windows = Windows()

        for window_option in WINDOW_OPTIONS:
            if car_detail is not None:
                option = car_detail.get(window_option)
                option_status = CarAttribute(option.get("value"),
                                             option.get("status"),
                                             option.get("ts"))
                setattr(windows, window_option, option_status)
            else:
                _LOGGER.warning("get_windows for %s failed", car_id)        
                setattr(windows, window_option, CarAttribute(-1, -1, None))

        return windows

    def get_doors(self, car_detail, car_id):
        _LOGGER.debug("get_doors for %s called", car_id)

        doors = Doors()

        for door_option in DOOR_OPTIONS:
            if car_detail is not None:
                option = car_detail.get(door_option)
                option_status = CarAttribute(option.get("value"),
                                             option.get("status"),
                                             option.get("ts"))
                setattr(doors, door_option, option_status)
            else:
                _LOGGER.warning("get_doors for %s failed", car_id)        
                setattr(doors, door_option, CarAttribute(-1, -1, None))

        return doors

    def get_electric(self, car_detail, car_id):
        _LOGGER.debug("get_electric for %s called", car_id)

        electric = Electric()

        for electric_option in ELECTRIC_OPTIONS:
            if car_detail is not None:
                option = car_detail.get(electric_option)
                option_status = CarAttribute(option.get("value"),
                                             option.get("status"),
                                             option.get("ts"))
                setattr(electric, electric_option, option_status)
            else:
                _LOGGER.warning("get_electric for %s failed", car_id)        
                setattr(electric, electric_option, CarAttribute(-1, -1, None))

        return electric

    def get_location(self, car_id):
        """ get refreshed location information."""
        _LOGGER.debug("get_location for %s called", car_id)

        api_result = self._retrieve_api_result(car_id, "location/v2")

        _LOGGER.debug("get_location result: %s", api_result)

        location = Location()

        for loc_option in LOCATION_OPTIONS:
            if api_result is not None:
                curr_loc_option = api_result.get("data").get(loc_option)
                value = CarAttribute(
                    curr_loc_option.get("value"),
                    curr_loc_option.get("status"),
                    curr_loc_option.get("ts"))

                setattr(location, loc_option, value)
            else:
                setattr(location, loc_option, CarAttribute(-1, -1, None))

        return location

    def get_tires(self, car_detail, car_id):
        # Get tire status.
        _LOGGER.debug("get_tires for %s called", car_id)

        tires = Tires()

        for tire_option in TIRE_OPTIONS:
            if car_detail is not None:
                curr_tire = car_detail.get(tire_option)
                curr_tire_status = CarAttribute(
                    curr_tire.get("value"),
                    curr_tire.get("status"),
                    curr_tire.get("ts")
                )
                setattr(tires, tire_option, curr_tire_status)
            else:
                setattr(tires, tire_option, CarAttribute(-1, -1, None))

        return tires


    def _get_session_cookies(self, username, password):
        # Start session and get login form.
        session = self.session
        loginpage = session.get(LOGIN_STEP1_URL, verify=LOGIN_VERIFY_SSL_CERT)

        # Get the hidden elements and put them in our form.
        login_html = lxml.html.fromstring(loginpage.text)
        hidden_elements = login_html.xpath('//form//input')
        form = {x.attrib['name']: x.attrib['value'] for x in hidden_elements}

        # "Fill out" the form.
        form['username'] = username
        form['password'] = password
        form['remember-me'] = 1

        # login and check the values.
        url = "{0}{1}".format(SERVER_LOGIN, LOGIN_STEP2_URL)
        loginpage2 = session.post(url, data=form, verify=LOGIN_VERIFY_SSL_CERT)

        _LOGGER.info(
            "Login step 2 http code %s", loginpage2.status_code)

        # step 3
        login2_html = lxml.html.fromstring(loginpage2.text)
        hidden_elements = login2_html.xpath('//form//input')
        form = {x.attrib['name']: x.attrib['value'] for x in hidden_elements}

        if DEBUG_MODE:
            file = open("LoginStep2.txt", "w")
            file.write(loginpage2.text)
            file.close()

        loginpage3 = session.post(LOGIN_STEP3_URL,
                                  data=form,
                                  verify=LOGIN_VERIFY_SSL_CERT)

        _LOGGER.info(
            "Login step 3 http code %s", loginpage3.status_code)

        if DEBUG_MODE:
            file = open("LoginStep3.txt", "w")
            file.write(loginpage3.text)
            file.close()

        self.is_valid_session = True
        return session.cookies

    def _retrieve_api_result(self, car_id, api):
        return self._retrieve_json_at_url(
            "{}/{}/{}/{}".format(
                SERVER_APP,
                API_VEHICLES,
                car_id,
                api))

    def _retrieve_json_at_url(self, url):
        try:
            _LOGGER.debug("Connect to URL %s", str(url))
            res = self.session.get(url, verify=LOGIN_VERIFY_SSL_CERT)
        except requests.exceptions.Timeout:
            _LOGGER.exception(
                "Connection to the api timed out at URL %s", API_VEHICLES)
            return
        if res.status_code != 200 and res.status_code != 403:
            _LOGGER.exception(
                "Connection failed with http code %s", res.status_code)
            return
        if res.status_code == 403:
            _LOGGER.warning(
                "Session invalid, will try to relogin, http code %s",
                res.status_code)
            self.is_valid_session = False
            self.session = None
            self.session = requests.session()
            self._get_session_cookies(self.username, self.password)
            return
        _LOGGER.debug("Connect to URL %s Status Code: %s Content: %s", str(url),
                      str(res.status_code), res.text)
        return res.json()
