# pylint: disable=too-many-public-methods
"""
OpenTmiClient module
"""
# standard imports
import json
import os
# 3rd party imports
# import deprecation
# Application imports
from opentmi_client.utils import is_object_id, get_logger
from opentmi_client.utils import requires_logged_in
from opentmi_client.utils import OpentmiException, TransportException
from opentmi_client.utils.decorators import setter_rules
from opentmi_client.transport import Transport
from opentmi_client.api.result import Result
from opentmi_client.api.build import Build
from opentmi_client.api.event import Event


REQUEST_TIMEOUT = 30

ENV_GITHUB_ACCESS_TOKEN = "OPENTMI_GITHUB_ACCESS_TOKEN"
ENV_OPENTMI_USERNAME = "OPENTMI_USERNAME"
ENV_OPENTMI_PASSWORD = "OPENTMI_PASSWORD"


# pylint: disable-msg=too-many-arguments
def create(host='localhost', port=None, result_converter=None,
           testcase_converter=None, logger=None):
    """
    Generic create -api for Client
    :param host:
    :param port:
    :param result_converter: optional converter function
    :param testcase_converter: optional converter function
    :param logger: optional logging instance
    :return: OpenTmiClient
    """
    client = OpenTmiClient(host, port, logger)
    client.set_result_converter(result_converter)
    client.set_tc_converter(testcase_converter)
    return client


class OpenTmiClient(object):
    """
    OpenTmiClient object
    """
    __version = 0
    __api = "/api/v"

    # pylint: disable-msg=too-many-arguments
    def __init__(self,
                 host='127.0.0.1',
                 port=None,
                 transport=None,
                 logger=None):
        """
        Constructor for OpenTMI client
        :param host: opentmi host address (default="localhost")
        :param port: opentmi server port (default=3000)
        :param transport: optional Transport layer. Mostly for testing purpose
        :param logger: optional Logging instance.
        """
        self.__logger = logger or get_logger()
        self.__transport = Transport(host, port) if not transport else transport
        # backward compatibility
        self.__result_converter = None
        self.__tc_converter = None
        self.try_login()

    def set_result_converter(self, func):
        """
        Set custom result converter
        :param func: conversion function
        :return: None
        """
        self.__result_converter = func

    def set_tc_converter(self, func):
        """
        Set custom test case converter
        :param func: conversion function
        :return: None
        """
        self.__tc_converter = func

    def login(self, username, password):
        """
        Login to OpenTMI server
        :param username: username for OpenTMI
        :param password: password for OpenTMI
        :return: OpenTmiClient
        """
        payload = {
            "email": username,
            "password": password
        }
        url = self.__resolve_url("/auth/login")
        response = self.__transport.post_json(url, payload)
        token = response.get("token")
        self.logger.info("Login success. Token: %s", token)
        self.set_token(token)
        return self

    def login_with_access_token(self, access_token, service="github"):
        """
        Login to OpenTMI server using access token
        :param access_token: access token to be used
        :param service: access token provider
        :return: OpenTmiClient
        """
        payload = {
            "access_token": access_token
        }
        url = "{}/auth/{}/token".format(self.__transport.host, service)
        self.logger.debug("Login using %s token", service)
        response = self.__transport.post_json(url, payload)
        token = response.get("token")
        self.logger.info("Login success. Token: %s", token)
        self.set_token(token)
        return self

    @property
    def is_logged_in(self):
        """
        get logged in state
        :return: boolean true if logged in.
        """
        return self.__transport.has_token()

    def set_logger(self, logger):
        """
        Set custom logger
        :param logger: logging.Logger instance
        :return: OpenTmiClient
        """
        self.__logger = logger
        return self

    @property
    def logger(self):
        """
        getter for logger
        :return: Logger
        """
        return self.__logger

    def logout(self):
        """
        Logout
        :return: OpenTmiClient
        """
        self.__transport.set_token(None)
        return self

    def set_token(self, token):
        """
        Set authentication token for transport layer
        :param token:
        :return: OpenTmiClient
        """
        self.__transport.set_token(token)
        return self

    def get_version(self):
        """
        Get Client version
        :return:
        """
        return self.__version

    @requires_logged_in
    @setter_rules(value_type=Event)
    def post_event(self, event):
        """
        Send build
        :param build: Build object
        :return: Stored build data
        """
        payload = event.data
        url = self.__resolve_apiuri("/events")
        try:
            data = self.__transport.post_json(url, payload)
            self.logger.debug("Event uploaded successfully, _id: %s", data.get("_id"))
            return data
        except TransportException as error:
            self.logger.warning("Event upload failed: %s (status: %s)", error.message, error.code)
        except OpentmiException as error:
            self.logger.warning(error)
        return None

    # @requires_logged_in
    @setter_rules(value_type=Build)
    def post_build(self, build):
        """
        Send build
        :param build: Build object
        :return: Stored build data
        """
        payload = build.data
        url = self.__resolve_apiuri("/duts/builds")
        try:
            data = self.__transport.post_json(url, payload)
            self.logger.debug("build uploaded successfully, _id: %s", data.get("_id"))
            return data
        except TransportException as error:
            self.logger.warning("Result upload failed: %s (status: %s)", error.message, error.code)
        except OpentmiException as error:
            self.logger.warning(error)
        return None

    # @requires_logged_in
    def upload_build(self, build):
        """
        Upload build
        :param build:
        :return:
        """
        build_dict = build
        build = Build()
        build.set_data(build_dict)
        return self.post_build(build)

    # Suite
    # @requires_logged_in
    def get_suite(self, suite, options=''):
        """
        get single suite informations
        :param suite:
        :param options:
        :return:
        """
        try:
            campaign_id = self.__get_campaign_id(suite)
        except OpentmiException as error:
            self.logger.warning("exception happened while resolving suite: %s, %s",
                                suite, error)
            return None

        if campaign_id is None:
            self.logger.warning("could not resolve campaign id for suite: %s",
                                suite)
            return None

        suite = self.__get_suite(campaign_id, options)
        return suite

    # Campaign

    # @requires_logged_in
    def get_campaigns(self):
        """
        Get campaigns
        :return:
        """
        return self.__get_campaigns()

    # @requires_logged_in
    def get_campaign_names(self):
        """
        Get campaign names
        :return:
        """
        campaigns = self.__get_campaigns()
        campaign_names = []
        for campaign in campaigns:
            campaign_names.append(campaign['name'])
        return campaign_names

    # @requires_logged_in
    def get_testcases(self, filters=None):
        """
        Get testcases
        :param filters:
        :return:
        """
        return self.__get_testcases(filters)

    # @requires_logged_in
    def update_testcase(self, metadata):
        """
        update test case
        :param metadata:
        :return:
        """
        testcase = self.__lookup_testcase(metadata['tcid'])
        if testcase:
            test_id = testcase.get('_id')
            self.logger.info("Update existing TC (%s)", test_id)
            self.__update_testcase(test_id, metadata)
        else:
            self.logger.info("Create new TC")
            self.__create_testcase(metadata)
        return self

    # @requires_logged_in
    @setter_rules(value_type=Result)
    def post_result(self, result):
        """
        Post Result object
        :param result: Result or plain dictionary
        :return:
        """
        url = self.__resolve_apiuri("/results")
        payload = result.data
        try:
            files = None
            # hasLogs, logFiles = result.hasLogs()
            # if hasLogs:
            #    zipFile = self.__archiveLogs(logFiles)
            #    self.logger.debug(zipFile)
            #    files = {"file": ("logs.zip", open(zipFile), 'rb') }
            #    self.logger.debug(files)
            data = self.__transport.post_json(url, payload, files=files)
            self.logger.debug("result uploaded successfully, _id: %s", data.get("_id"))
            return data
        except TransportException as error:
            self.logger.warning("result uploaded failed: %s. status_code: %d",
                                error.message, error.code)
        except OpentmiException as error:
            self.logger.warning(error)
        return None

    # @deprecation.deprecated(deprecated_in="v0.4.0", removed_in="v0.5.0",
    #                        details="Use post_result(Result) instead")
    def upload_results(self, result):
        """
        Upload result, and test case if not stored already
        :param result: dictionary
        :return: Dictionary
        """
        tc_meta = self.__tc_converter(result.tc_metadata) if self.__tc_converter else result
        test_case = self.__lookup_testcase(tc_meta['tcid'])
        if not test_case:
            test_case = self.__create_testcase(tc_meta)
            if not test_case:
                self.logger.warning("TC creation failed")
                return None

        result_dict = self.__result_converter(result) if self.__result_converter else result
        result = Result()
        result.set_data(result_dict)
        return self.post_result(result)

    def try_login(self, raise_if_fail=False):
        """
        function to check if login is done.
        If not try to use environment variables by default
        :param raise_if_fail: Boolean, raise if login failed
        or env variables are does not exists. Default False
        :return: OpenTmiClient
        :throws: OpentmiException in case of failure
        """
        # use environment variables if available
        token = os.getenv(ENV_GITHUB_ACCESS_TOKEN)
        if token:
            self.logger.info("Using github access token from environment variable")
            return self.login_with_access_token(access_token=token, service="github")
        username = os.getenv(ENV_OPENTMI_USERNAME)
        password = os.getenv(ENV_OPENTMI_PASSWORD)
        if username and password:
            self.logger.info("Using opentmi credentials from environment variable")
            return self.login(username, password)
        if raise_if_fail:
            raise OpentmiException("login required")
        return self

    # Private members

    # @requires_logged_in
    def __get_campaign_id(self, campaign_name):
        """
        get campaign id from name
        :param campaign_name:
        :return: string
        """
        if is_object_id(campaign_name):
            return campaign_name

        for campaign in self.__get_campaigns():
            if campaign['name'] == campaign_name:
                return campaign['_id']
        return None

    def __get_testcases(self, filters=None):
        url = self.__resolve_apiuri("/testcases")
        return self.__transport.get_json(url, params=filters if filters else None)

    def __get_campaigns(self):
        url = self.__resolve_apiuri("/campaigns")
        return self.__transport.get_json(url, params={"f": "name"})

    def __get_suite(self, suite, options=''):
        url = self.__resolve_apiuri("/campaigns/" + suite + "/suite" + options)
        return self.__transport.get_json(url)

    def __lookup_testcase(self, tcid):
        url = self.__resolve_apiuri("/testcases")
        self.logger.debug("Search TC: %s", tcid)
        try:
            data = self.__transport.get_json(url, params={"tcid": tcid})
            if len(data) == 1:
                doc = data[0]
                self.logger.debug("testcase '%s' exists in DB (%s)", tcid, doc.get('_id'))
                return doc
        except TransportException as error:
            if error.code == 404:
                self.logger.warning("testcase '%s' not found form DB", tcid)
            else:
                self.logger.warning("Test case find failed: %s", error.message)
        except OpentmiException as error:
            self.logger.warning(error)

        return None

    def __update_testcase(self, test_id, metadata):
        url = self.__resolve_apiuri("/testcases/" + test_id)
        try:
            self.logger.debug("Update TC: %s", url)
            payload = metadata
            data = self.__transport.put_json(url, payload)
            self.logger.debug("testcase metadata uploaded successfully")
            return data
        except TransportException as error:
            self.logger.debug(error)
        except OpentmiException as error:
            self.logger.debug(error)

        self.logger.warning("testcase metadata upload failed")
        return None

    def __create_testcase(self, metadata):
        url = self.__resolve_apiuri("/testcases")
        try:
            self.logger.debug("Create TC: %s", url)
            payload = metadata
            data = self.__transport.post_json(url, payload)
            self.logger.debug("new testcase metadata uploaded successfully with id: %s",
                              json.dumps(data))
            return data
        except TransportException as error:
            self.logger.warning(error)
        except OpentmiException as error:
            self.logger.warning('createTestcase throw exception:')
            self.logger.warning(error)

        self.logger.warning("new testcase metadata upload failed")
        return None

    def __resolve_url(self, path):
        return self.__transport.get_url(path)

    def __resolve_apiuri(self, path):
        return self.__resolve_url(self.__api + str(self.__version) + path)
