import requests
import json

from errors import ArgumentMissingError, HTTPError


class Client(object):
    """ PyOpenCell class
    """

    def __init__(self,
                 baseurl=None,
                 username=None,
                 password=None):
        if not baseurl:
            raise ArgumentMissingError("baseurl")
        self.baseurl = baseurl.rstrip("/")
        self.api_route = "/api/rest"
        if not username:
            raise ArgumentMissingError("username")
        self.username = username
        if not password:
            raise ArgumentMissingError("password")
        self.password = password

        self.http_method = None

    def find_customer(self,
                      customer_id=None):
        """ Find a Customer

        Args:
            customer_id (int): Customer ID to find

        Return:
            **response**: Return the response object
        """
        if not customer_id:
            raise ArgumentMissingError("customer_id")

        self.url = "{0}{1}/account/customerAccount/list?customerCode={2}".format(
            self.baseurl,
            self.api_route,
            str(customer_id))
        self.http_method = 'GET'

        response = self._send_request()

        return response

    def create_subscription(
            self,
            subscription=None):
        """ Create a Subscription

        Args:
            subscription (dict): Dict with the Customer Account Hierarchy fields

        Return:
            **response**: Return the response object
        """
        if not subscription:
            raise ArgumentMissingError("subscription")

        self.url = "{0}{1}/billing/subscription".format(
            self.baseurl,
            self.api_route)
        self.http_method = 'POST'

        response = self._send_request(subscription)

        return response

    def create_or_update_account_hierarchy(
            self,
            customer_hierarchy=None):
        """ Create or Update Customer Account Hierarchy

        Args:
            customer_hierarchy (dict): Dict with the Customer Account Hierarchy fields

        Return:
            **response**: Return the response object
        """
        if not customer_hierarchy:
            raise ArgumentMissingError("account_hierarchy")

        self.url = "{0}{1}/account/accountHierarchy/createOrUpdateCRMAccountHierarchy".format(
            self.baseurl,
            self.api_route)
        self.http_method = 'POST'

        response = self._send_request(customer_hierarchy)

        return response

    def _send_request(self, payload=None):
        """send the API request using the *requests.request* method

        Args:
            payload (dict)

        Raises:
            OTRSHTTPError:
            ArgumentMissingError

        Returns:
            **requests.Response**: Response received after sending the request.

        .. note::
            Supported HTTP Methods: DELETE, GET, HEAD, PATCH, POST, PUT
        """
        headers = {"Content-Type": "application/json"}

        json_payload = json.dumps(payload)

        try:
            response = requests.request(self.http_method.upper(),
                                        self.url,
                                        headers=headers,
                                        data=json_payload,
                                        auth=(self.username, self.password))

            # store a copy of the request
            self._request = response.request

        # critical error: HTTP request resulted in an error!
        except Exception as err:
            # raise OTRSHTTPError("get http")
            raise HTTPError("Failed to access OpenCell. Check Hostname!\n"
                            "Error with http communication: {0}".format(err))

        if not response.status_code == 200:
            raise HTTPError("Received HTTP Error. Check Hostname and WebServiceName.\n"
                            "HTTP Status Code: {0.status_code}\n"
                            "HTTP Message: {0.content}".format(response))
        return response
