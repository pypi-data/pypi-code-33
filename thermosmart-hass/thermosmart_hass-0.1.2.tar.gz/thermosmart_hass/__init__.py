from . import oauth2
import requests
import json

class ThermoSmart(object):
    """ 
    Class represents the Thermosmart thermostat
    """

    def __init__(self, token=None):

        self._session = requests.Session()
        self._token = token
        self.prefix = 'https://api.thermosmart.com/'
        self.id = self._get_thermostat_id()

    def _internal_call(self, method, url, headers, payload):
        args = dict()
        url = self.prefix + url + '?access_token=' + self._token
        if payload:
            args['data'] = json.dumps(payload)

        if headers:
            args['headers'] = headers

        r = self._session.request(method, url, **args)

        if r.status_code != requests.codes['ok']:
            r.raise_for_status()

        return r.json()

    def _get(self, url, args=None, payload=None):
        return self._internal_call('GET', url, None, payload)

    def _put(self, url, args=None, payload=None):
        return self._internal_call('PUT', url, {"Content-Type": "application/json"}, payload)

    def _post(self, url, args=None, payload=None):
        return self._internal_call('POST', url, {"Content-Type": "application/json"}, payload)
            
    def _get_thermostat_id(self):
        return (self._get('thermostat'))['hw']

    def request_thermostat(self):
        result = self._get('thermostat/' + self.id)
        if result.get('ot'):
            if result['ot']['enabled']:
                result['ot']['readable'] = self.convert_ot_data(result['ot']['raw'])
        return result

    def name(self):
        return self.request_thermostat()['name']

    def room_temperature(self):
        return self.request_thermostat()['room_temperature']

    def target_temperature(self):
        return self.request_thermostat()['target_temperature']

    def outside_temperature(self):
        return self.request_thermostat()['outside_temperature']
    
    def programs(self):
        return self.request_thermostat()['programs']
    
    def schedule(self):
        return self.request_thermostat()['schedule']

    def exceptions(self):
        return self.request_thermostat()['exceptions']

    def source(self):
        return self.request_thermostat()['source']

    def firmwware(self):
        return self.request_thermostat()['fw']

    def opentherm(self):
        result = self.request_thermostat()
        if result.get('ot'):
            if result['ot']['enabled']:
                return self.convert_ot_data(result['ot']['raw'])
            else:
                return None

    def location(self):
        return self.request_thermostat()['location']

    def outside_temperature_icon(self):
        return self.request_thermostat()['outside_temperature_icon']

    def geofence_devices(self):
        return self.request_thermostat()['geofence_devices']

    def geofence_enabled(self):
        return self.request_thermostat()['geofence_enabled']

    def set_target_temperature(self,temperature):
        self._put('thermostat/' + self.id, payload={"target_temperature": temperature})

    def set_exceptions(self, exceptions):
        """
        exceptions must be a list that contains the blocks for the exceptions to the week schedule. 
        Each block (element) is an json object than contains start (starting time), end (end time), temperature and desciption (optional). 
        Start and end are 5-element lists of year, month [0-11], day [1-31], hours [0-23] and minutes [0, 15, 30, 45]
        Temperature is the name of a temperature program (anti_freeze, not_home, home, comfort, pause)
        Description a short discription, maximum 30 characters
        Example:
        [{"start":[2014,3,26,21,30],"end":[2014,3,27,0,30],"temperature":"home"}]
        """
        self._put('thermostat/' + self.id, payload={"exceptions": exceptions})
    
    def set_schedule(self, schedule):
        """
        schedule must be a list that contains the blocks for the week schedule. 
        Each block (element) is an json object than contains start (staring time) and temperature. 
        Start is a 3-element list of day (0=monday), hours and mintues
        Temperature is the name of a temperature program (anti_freeze, not_home, home, comfort, pause)
        Example:
        [{"start":[6,5,30],"temperature":"home"}, {"start":[6,9,0],"temperature":"not_home"}]
        """
        self._put('thermostat/' + self.id, payload={"schedule": schedule})
    
    def set_programs(self, programs):
        """
        program must be a 5 element json object that must contains following temperatures:
        anti_freeze, not_home, home, comfort, pause
        Example:
        {"anti_freeze":12,"not_home":15,"home":19,"comfort":22,"pause":5}
        """
        self._put('thermostat/' + self.id, payload={"schedule": programs})

    def set_outside_temperature(self, temperature):
        self._put('thermostat/' + self.id, payload={"outside_temperature": temperature})

    def set_room_temperature(self, temperature):
        self._put('thermostat/' + self.id, payload={"room_temperature": temperature})

    def set_geofence_enabled(self, enabled):
        self._put('thermostat/' + self.id, payload={"geofence_enabled": enabled})

    def pause_thermostat(self, yesno):
        self._post('thermostat/' + self.id +'/pause', payload={"pause": yesno})

    def webhook(self, webhook):
        self._post('webhook', payload={"webhook": webhook})

    def convert_ot_data(self, data):
        converted_data = dict()
        # Convert ot0
        if data.get('ot0'):
            converted_data['CH_enabled'] = True if bytes.fromhex(data['ot0'][2:])[0] & 1 == 1 else False
            converted_data['DHW_enabled'] = True if bytes.fromhex(data['ot0'][2:])[0] & 2 == 2 else False 
            converted_data['Cooling_enabled'] = True if bytes.fromhex(data['ot0'][2:])[0] & 4 == 4 else False 
            converted_data['OTC_active'] = True if bytes.fromhex(data['ot0'][2:])[0] & 8 == 8 else False 
            converted_data['CH2_enabled'] = True if bytes.fromhex(data['ot0'][2:])[0] & 16 == 16 else False 
            converted_data['Summer_winter_mode'] = True if bytes.fromhex(data['ot0'][2:])[0] & 32 == 32 else False 
            converted_data['DHW blocked'] = True if bytes.fromhex(data['ot0'][2:])[0] & 64 == 64 else False 
        # Convert ot1
        if data.get('ot1'):
            converted_data['Control_setpoint'] = self._convert_f88_to_float(data['ot1'])
        # Convert ot3
        if data.get('ot3'):
            converted_data['DHW_present'] = True if bytes.fromhex(data['ot3'][2:])[0] & 1 == 1 else False
            converted_data['Control_type'] = 'on/off' if bytes.fromhex(data['ot3'][2:])[0] & 2 == 2 else 'modulating' 
            converted_data['Cooling_config'] = True if bytes.fromhex(data['ot3'][2:])[0] & 4 == 4 else False 
            converted_data['DHW_config'] = 'storage_tank' if bytes.fromhex(data['ot3'][2:])[0] & 8 == 8 else 'instantaneous' 
            converted_data['pump_control'] = False if bytes.fromhex(data['ot3'][2:])[0] & 16 == 16 else True 
            converted_data['CH2_present'] = True if bytes.fromhex(data['ot3'][2:])[0] & 32 == 32 else False 
            converted_data['remote_water_fill'] = False if bytes.fromhex(data['ot3'][2:])[0] & 64 == 64 else True 
            converted_data['heat_cool_control'] = 'master' if bytes.fromhex(data['ot3'][2:])[0] & 128 == 128 else 'slave' 
        # Convert ot17
        if data.get('ot17'):
            converted_data['Modulation_level'] = self._convert_f88_to_float(data['ot17'])
        # Convert ot18
        if data.get('ot18'):
            converted_data['Water_pressure'] = self._convert_f88_to_float(data['ot18'])
        # Convert ot19
        if data.get('ot19'):
            converted_data['DHW_flow_rate'] = self._convert_f88_to_float(data['ot19'])
        # Convert ot25
        if data.get('ot25'):
            converted_data['Boiler_temperature'] = self._convert_f88_to_float(data['ot25'])
        # Convert ot26
        if data.get('ot26'):
            converted_data['DHW_temperature'] = self._convert_f88_to_float(data['ot26'])
        # Convert ot27
        if data.get('ot27'):
            converted_data['Outside_temperature'] = self._convert_f88_to_float(data['ot27'])
        # Convert ot28
        if data.get('ot28'):
            converted_data['Return_water_temperature'] = self._convert_f88_to_float(data['ot28'])
        # Convert ot34
        if data.get('ot34'):
            converted_data['Heat_exchanger_temperature'] = self._convert_f88_to_float(data['ot34'])
        # Convert ot56
        if data.get('ot56'):
            converted_data['DWH_setpoint'] = self._convert_f88_to_float(data['ot56'])
        # Convert ot125
        if data.get('ot125'):
            converted_data['OT_version'] = self._convert_f88_to_float(data['ot125'])

        return converted_data

    def _convert_f88_to_float(self,f88):
        return int.from_bytes(bytes.fromhex(f88[2:]),'big',signed=True)/256
