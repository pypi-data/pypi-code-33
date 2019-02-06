import requests
from datetime import datetime
from requests_futures.sessions import FuturesSession


class RequestError(Exception):
    def __init__(self,message):
        super(Exception,self).__init__(message)
        self.message = message


class Client(object):
    REFRESH = 240 # 4 minutes less than time out for async request compatibility
    GET = "GET"
    POST = "POST"
    FORMAT_JSON = "application/json"
    FORMAT_XML = "application/json"

    def __init__(self, server_url:str,
                 username:str,
                 password:str,
                 format:str = FORMAT_JSON):
        self.login_headers = {"Content-Type": "application/json"}
        self.username=username
        self.password=password
        self.login_data = {"username": self.username,"password": self.password}
        self.server_url = server_url + "/" if server_url[-1] != "/" else server_url
        self.session = None  # request session  or future session
        self.refresh_time = None  # str: refresh token
        self.last_request = None  # last datetime of a request
        self.header_format=format

    def refresh(self):
        """
        refresh authentication token
        :return:
        """
        headers=[]
        headers["Content-Type"]=self.header_format
        data = {"refresh":self.refresh_time}
        d = self.session.request_data(method="POST",
                                 path=self.server_url+"api/token-refresh/",
                                 json=data,
                                 headers=headers)
        self.access = d["access"]

    @staticmethod
    def get_actual_response(response):
        """
        will return actual data from request
        :return:
        """
        raise NotImplemented("not implemented")

    def initialize(self):
        """
        initializes tokens and timeouts
        call _set_keys after making request for authorization
        :return:
        """
        raise NotImplemented("not implemented")

    def _set_keys(self, response:requests.Response):
        if response.status_code == requests.codes.ok:
            self.access = response.json()["access"]
            self.refresh_time = response.json()["refresh"]
            self.last_request = datetime.now()
        else:
            raise RequestError("set keys failed: " + str(response.status_code) + " " + str(response.text))


class AsyncClient(Client):
    def __init__(self,server_url:str,username:str,password:str):
        super(AsyncClient,self).__init__(server_url,username,password)
        self.session = FuturesSession()
        self.initialize()

    def initialize(self):
        future = self.session.post(self.server_url+"api/token-auth/",
                                   json=self.login_data,
                                   headers=self.login_headers)
        r = future.result()
        self._set_keys(self.get_actual_response(r))

    @staticmethod
    def get_actual_response(response):
        """
        returns the actual response from the future
        :param self:
        :param response:
        :return:
        """
        return response.result()


class SyncClient(Client):

    def __init__(self,server_url:str,username:str,password:str):
        super(SyncClient,self).__init__(server_url,username,password)
        self.session = requests.session()
        self.initialize()

    def initialize(self):
        r = self.session.post(self.server_url+"api/token-auth/",
                              json=self.login_data, headers=self.login_headers)
        self._set_keys(self.get_actual_response(r))

    @staticmethod
    def get_actual_response(response):
        """
        returns the response
        :param response:
        :return:
        """
        return response

