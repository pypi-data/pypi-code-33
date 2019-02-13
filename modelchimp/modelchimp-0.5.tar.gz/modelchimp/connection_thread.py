import os
import json
import websocket
import requests
import logging

from time import sleep
from threading import Thread, Event

from .enums import ExperimentStatus


class WSConnectionThread(Thread):
    PROTOCOL = "wss://"

    def __init__(self, address):
        super(WSConnectionThread, self).__init__()
        self.stopped = False
        self.daemon = True
        self.address = address
        self.ws = self.connect()
        self.dummy_event = Event()
        self.logger = logging.getLogger(__name__)

    def run(self):
        while not self.stopped:
            try:
                self.ws.run_forever()
            except Exception as e:
                time.sleep(0.3)

    def stop(self):
        self.stopped = True
        self.ws.close()

    def connect(self):
        ws = websocket.WebSocketApp(self.PROTOCOL + self.address,
                                  on_message = self.on_message,
                                  on_error = self.on_error,
                                  on_close = self.on_close)
        ws.open = self.on_open
        return ws

    def on_message(self, ws, message):
        self.logger.info("Realtime connection established with ModelChimp Server.")
        pass

    def on_error(self, ws, error):
        #print(error)
        pass

    def on_close(self, ws):
        #print("### closed ###")
        pass

    def on_open(self, ws):
        while self.stopped is True:
            self.stop()
        pass

    def send(self, event):
        self.connection_wait()

        # If the connection does not exist then put event back into the queue
        if self.is_connected():
            json_data = json.dumps({'message': event}, cls=ParamEncoder, allow_nan=False)
            self.ws.send(json_data)

    def is_connected(self):
        if self.ws.sock is not None:
            try:
                return self.ws.sock.connected
            except AttributeError:
                pass

        return False

    def connection_wait(self):
        count = 0
        while not self.is_connected() and count < 10 and not self.stopped:
                sleep(1)
                self.logger.info("Tring to Connect. Attempt %s" % (count+1, ))
                count += 1

        return True

    @classmethod
    def set_protocol(cls, protocol):
        cls.PROTOCOL = protocol


class RestConnection:
    PROTOCOL = "https://"

    def __init__(self, address, key):
        self.address = address
        self.key = key
        self.project_id = ''
        self.model_id = ''
        self.session = requests.Session()
        self._http_headers = {}
        self._connected = False
        self.logger = logging.getLogger(__name__)

        if self._check_connection(): self._authenticate(key)


    def _check_connection(self,):
        self.logger.info("Establishing connection with ModelChimp Server.")

        # Check https is working
        if os.getenv('MODELCHIMP_DEBUG') != 'True':
            try:
                self.session.get(self.PROTOCOL + self.address, timeout=(3.5, None))
                return True
            except (requests.exceptions.ConnectionError,requests.exceptions.ReadTimeout):
                pass

        # Check http is working
        try:
            self.PROTOCOL = "http://"
            self.session.get(self.PROTOCOL + self.address)

            # Update the websocket protocol
            WSConnectionThread.set_protocol("ws://")
            return True
        except requests.exceptions.ConnectionError:
            self.logger.info("ModelChimp Server is not accessible. Current experiment won't be logged.")

        return False

    def _authenticate(self, key):
        authentication_url = self.PROTOCOL + self.address + 'api/decode-key/'
        auth_data = {"key": key}
        response_auth = None

        response_auth = self.session.post(authentication_url,
                                                data=auth_data)

        # Check if the request got authenticated
        if response_auth.status_code != 200:
            raise requests.exceptions.RequestException(
                "Authentication failed. Have you added the correct key")

        # Get the authenticated token and assign it to the header
        token = json.loads(response_auth.text)['token']
        self._connected = True
        self._http_headers = {'Authorization': 'Token ' + token}
        self.project_id = json.loads(response_auth.text)['project_id']

    def post(self,url, data, files=None):
        url = self.PROTOCOL + self.address + url

        if files:
            request = self.session.post(url, data=data,
                            files=files,
                            headers=self._http_headers)
        else:
            request = self.rest.session.post(url, data=data,
                            headers=self._http_headers)

        return request

    def get(self,url):
        url = self.PROTOCOL + self.address + url

        request = self.session.get(url, headers=self._http_headers)

        return request

    def create_experiment(self, experiment_id, experiment_name,  filename):
        if not self._connected:
            return False

        ml_model_url =  self.PROTOCOL + "%s%s%s/" % (self.address,
                                    'api/create-experiment/',
                                     self.project_id)
        result = {
            'experiment_id' : experiment_id,
            'project' : self.project_id,
            'name': experiment_id,
            'status' : ExperimentStatus.IN_PROCESS
        }

        if experiment_name: result['name'] = experiment_name

        try:
            if filename:
                with open(filename, 'rb') as f:
                    save_request = self.session.post(ml_model_url, data=result,
                    files={"code_file": f}, headers=self._http_headers)
            else:
                save_request = self.session.post(ml_model_url, data=result,
                headers=self._http_headers)

            self.model_id = json.loads(save_request.text)['model_id']
            self.logger.info('Experiment is live at %s%smodel-detail/%s' % (self.PROTOCOL,
                                                                            self.address,
                                                                            self.model_id))
            return True
        except Exception:
            self.logger.error("Failed to created experiment")

        return False

    def create_data_version(self, version_id, data, file_locations):
        if not self._connected:
            return False
        print(file_locations)
        url =  self.PROTOCOL + "%s%s%s/" % (self.address,
                                    'api/create-data-version/',
                                     self.project_id)
        result = {
            'version_id' : version_id,
            'project' : self.project_id,
            'name': version_id,
            'files': json.dumps(file_locations)
        }

        try:
            # with open(filename, 'rb') as f:
            self.logger.info('Data is getting uploaded')

            save_request = self.session.post(url, data=result,
            files={"files_path": data}, headers=self._http_headers)

            self.logger.info('Data successfully uploaded')
            return True
        except Exception as e:
            self.logger.error("Failed to load the data %s" %(e,))

        return False

class ParamEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
          json.JSONEncoder().encode(obj)
          return obj
        except Exception as e:
          # if its function, get the name
          obj_name = getattr(obj, '__name__', None)

          # if its a class, get the name
          if not obj_name and hasattr(obj, '__class__'):
              obj_name = getattr(obj.__class__, '__name__', None)

          if obj_name:
              obj = obj_name
          else:
              obj = str(obj)

        return obj
