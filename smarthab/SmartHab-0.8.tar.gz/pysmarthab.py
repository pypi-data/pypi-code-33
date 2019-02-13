#!/usr/bin/env python3

# smarthab-python - control devices in a SmartHab-powered home
# Copyright (C) 2019  Baptiste Candellier

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""SmartHab home automation Python module.

Allows users to control their SmartHab devices.
"""
import hmac
import collections
from dataclasses import dataclass
import uuid
import json
import abc
import enum
import logging

import requests

@dataclass
class State:
    """SmartHab login state, contains necessary info for authentication"""
    uid = uuid.uuid4()
    email = None
    token = None
    device = 'android'

class Endpoint(enum.Enum):
    """SmartHab API endpoints"""
    GET_TOKEN = 'getToken'
    GET_NOTIFICATIONS = 'getNotifications'
    GET_OBJECTS = 'getObjects'
    GET_WEATHER = 'getMTO'
    GET_SETTINGS = 'getReglages'
    GET_INFOS = 'getInfos'
    GET_DASHBOARD_MODE = 'getModeDashboard'
    GET_OBJECT_STATE = 'getStateObject'
    GET_POWER_CONSUMPTION = 'getConsoElec'
    GET_HEATING = 'getChauffage'
    GET_SCENARIOS = 'getScenarios'
    SET_OBJECT_STATE = 'setObject'

class _Security:
    """Security functions to handle SmartHab HMAC generation"""
    @staticmethod
    def hmac_list(key, parameters):
        """Signs a list of parameters and returns the HMAC as an hex string"""
        msg = _Security.params_to_query_string(parameters)
        return hmac.new(key.encode(), msg.encode(), 'sha256').hexdigest()

    @staticmethod
    def sign_params(key, parameters):
        """Adds HMAC signature to parameter list"""
        parameters.update({'sha': _Security.hmac_list(key, parameters)})
        return parameters

    @staticmethod
    def params_to_query_string(parameters):
        """Sorts a list of parameters and convert them into a query string, without
        urlencoding them
        """
        items = collections.OrderedDict(sorted(parameters.items()))
        joined_items = map(lambda key: f"{str(key)}={str(items[key])}", items)
        query_str = '&'.join(joined_items)
        return query_str

class _Network:
    """Network functions for SmartHab, designed to be mocked for testing"""
    # SmartHab root API URL
    _ROOT_URL = 'http://217.182.92.116/front/API'

    def __init__(self, security=_Security()):
        self.state = State()
        self._security = security

    def _default_key(self):
        return self.state.token + str(self.state.uid)

    def send_request(self, endpoint, params=None, key=None, verb='GET'):
        """Sends a request to the SmartHab API to the given endpoint,
        with the given parameters, key and HTTP verb.
        """
        if key is None:
            key = self._default_key()

        all_params = self._make_full_query_params(key, params)

        logging.debug("sending %s request to endpoint %s", verb, endpoint)

        res = requests.request(verb, f"{self._ROOT_URL}/{endpoint.value}/", params=all_params,
                               headers={'Accept': 'application/json'})

        if res.status_code in range(200, 300):
            return _Network._parse_response(res.text)

        logging.error("error while sending request, status code was %s", str(res.status_code))
        return None

    @staticmethod
    def _parse_response(response):
        if response == "":
            return response

        # API sometimes outputs PHP errors... sigh.
        # Only keep last line since JSON is only on one line anyway to remove
        # all that other garbage
        clean_text_res = response.splitlines()[-1]

        try:
            json_res = json.loads(clean_text_res)

            if isinstance(json_res, dict) and not json_res['success']:
                logging.error("request failed, response body: %s", clean_text_res)
                raise RequestFailedException

            return json_res
        except ValueError:
            return clean_text_res

    def _make_full_query_params(self, key, params):
        default_params = {
            'login': self.state.email,
            'device': self.state.device
        }

        if params is None:
            params = {}

        # Append login and device to required parameters
        params.update(default_params)

        # Sign the query, adding the SHA back to the param list
        return self._security.sign_params(key, params)

class SmartHab:
    """The SmartHab class allows you to interact with the SmartHab API,
    including logging in, getting a list of available devices, and managing
    their state.
    """
    def __init__(self, state=None, network=_Network()):
        self._network = network
        if state is not None:
            self._network.state = state
        self._state = self._network.state

    def login(self, email, password):
        """Logs in and stores the returned token in internal state."""
        self._state.token = None
        self._state.email = email

        params = {
            'cle': str(password),
            'uid': str(self._state.uid)
        }

        try:
            res = self._network.send_request(Endpoint.GET_TOKEN, params, str(password))
            self._state.token = res['token']
        except RequestFailedException:
            pass

    def is_logged_in(self):
        """Checks if the user was logged in successfully."""
        return self._state.token is not None

    def get_device_list(self):
        """Gets a list of all available devices."""
        if not self.is_logged_in():
            raise LoginRequiredException

        res = self._network.send_request(Endpoint.GET_OBJECTS)

        # Cleanup response by flattening all devices to the list's top level
        flat_devices = []
        SmartHab._flatten_devices_list(flat_devices, res['objects'])

        # Map each JSON device to a well-known device object
        parsed = list(map(self._device_factory, flat_devices))
        logging.debug("found a total of %s devices", len(parsed))

        # Cleanup unknown or unwanted device types that couldn't be parsed
        devices = list(filter(lambda x: x is not None, parsed))
        logging.debug("found %s supported devices", len(devices))

        return devices

    def _device_factory(self, device):
        family = int(device['id_famille'])

        if family == DeviceType.LIGHT:
            return Light(self._network, device['code'], device['objLabel'], device['pieceLabel'])

        if family == DeviceType.SHUTTER:
            return Shutter(self._network, device['code'], device['objLabel'], device['pieceLabel'])

        if family == DeviceType.THERMOSTAT:
            return Thermostat(self._network, device['code'], device['objLabel'],
                              device['pieceLabel'])

        return None

    @staticmethod
    def _flatten_devices_list(result, devices):
        """Take a list of devices all nested under different dicts associated
        to differents ids and flatten it into a simple list"""
        if 'code' in devices.keys():
            result.append(devices)
        else:
            for child in devices.values():
                if isinstance(child, list):
                    # Value is an array instead of a single object
                    for grandchild in child:
                        SmartHab._flatten_devices_list(result, grandchild)
                else:
                    SmartHab._flatten_devices_list(result, child)

class DeviceType(enum.IntEnum):
    """Defines supported types of devices in SmartHab."""
    LIGHT = 1
    SHUTTER = 3
    THERMOSTAT = 5
    SENSOR_TEMP = 6
    SENSOR_MOTION = 23
    SENSOR_LUMINANCE = 8
    SENSOR_RELHUMIDITY = 7
    ELECT_SWITCH = 22
    POWER_METER = 16
    SMOKE_DETECTOR = 10

class Device(abc.ABC):
    """A device with basic properties and an editable state."""
    def __init__(self, network, type_id, device_id, label, room_label):
        self._network = network
        self.type_id = type_id
        self.device_id = device_id
        self.label = label
        self.room_label = room_label

        self.cached_state = None

    @staticmethod
    def _sh_state_to_py_type(state):
        s = state.upper()

        if s in ('OFF', ''):
            return False
        if s == 'ON':
            return True
        if s == 'NULL':
            return None

        return int(s)

    @staticmethod
    def _py_state_to_sh_type(state):
        if isinstance(state, bool):
            if state:
                return 'ON'
            return 'OFF'

        if state is None:
            return 'NULL'

        return str(state)

    def update(self):
        """Retrieves and stores the device's current state."""
        res = self._network.send_request(Endpoint.GET_OBJECT_STATE,
                                         {'objet': self.device_id})
        self.cached_state = Device._sh_state_to_py_type(res)

    @property
    def state(self):
        """The device's state. Can be an int, a string, or a boolean."""
        return self.cached_state

    @state.setter
    def state(self, state):
        """Updates the device's state."""
        params = {
            'objet': self.device_id,
            'etat': Device._py_state_to_sh_type(state)
        }

        r_state = self._network.send_request(Endpoint.SET_OBJECT_STATE,
                                             params, verb='POST')
        self.cached_state = Device._sh_state_to_py_type(r_state)

class BinaryDevice(Device, abc.ABC):
    """A device with an OFF and an ON state."""
    def turn_off(self):
        """Turns off the device."""
        self.state = False

    def turn_on(self):
        """Turns on the device."""
        self.state = True

    def toggle(self):
        """Toggles the device's state."""
        self.state = not self.state

class Shutter(Device):
    """A device representing rolling shutters, with a state ranging from 0 to 100."""
    def __init__(self, network, device_id, label, room_label):
        super().__init__(network, DeviceType.SHUTTER, device_id, label, room_label)

    def close(self):
        """Closes the shutters."""
        self.state = 0

    def open(self):
        """Opens the shutters."""
        self.state = 100

class Light(BinaryDevice):
    """Represents a lightbulb with a binary ON/OFF state."""
    def __init__(self, network, device_id, label, room_label):
        super().__init__(network, DeviceType.LIGHT, device_id, label, room_label)

class Thermostat(Device):
    """Represents a thermostat."""
    def __init__(self, network, device_id, label, room_label):
        super().__init__(network, DeviceType.THERMOSTAT, device_id, label, room_label)

    def get_current_set_temp(self):
        """Returns the current set temperature. Not implemented."""

    def get_current_ambient_temp(self):
        """Returns the current ambient temperature. Not implemented."""

class RequestFailedException(Exception):
    """Raised when the response to a request was negative."""

class LoginRequiredException(Exception):
    """Raised when the user wasn't successfully authenticated and login is required."""

if __name__ == "__main__":
    pass
