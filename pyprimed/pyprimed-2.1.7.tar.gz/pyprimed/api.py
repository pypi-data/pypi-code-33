# -*- coding: utf-8 -*-
import re
import logging
import requests
import daiquiri
import uuid
import json

import pyprimed.util
from pyprimed.exceptions import *

daiquiri.setup(level=logging.INFO)

logger = daiquiri.getLogger(__name__)


class Client:
    def __init__(self, connection):
        self._connection = connection
        self._session = requests.Session()
        self._session.auth = (connection._username, connection._password)
        self._session.headers.update({"Content-type": "application/json"})
        self._session.headers.update(
            {"X-SESSION-UUID": str(uuid.uuid4())}
        )  # uniquely identifies this session

        self._user = self._auth()

    def _auth(self):
        try:
            result = self._session.get("{}/{}".format(self._connection.baseurl, "auth"))

            if result.status_code != 200:
                raise AuthenticationError()
            else:
                return result.json()
        except ConnectionRefusedError as e:
            # the url is valid syntax-wise, but no remote listening
            raise UnknownRemoteExpection()

    def _mark_done(self, path):
        logger.debug("marking transaction done on {}".format(path))

        response = self._session.post("{}{}".format(self._connection.baseurl, path))
        self._check_for_errors(response, 200, "MARK_DONE")

        return response.json()

    def _check_for_errors(self, response, status_code, opname):
        if response.headers["content-type"] != "application/json; charset=utf-8":
            rh = response.headers["content-type"]
            msg = "{opname}: expected response to be 'application/json; charset=utf-8', was {rh}".format(
                opname=opname, rh=rh
            )
            raise ServerError(msg)

        if response.status_code != status_code:
            response_body = response.json()

            if "errors" in response_body:
                errors = []
                for error in response_body["errors"]:
                    if "msg" in error:
                        errors.append(error["msg"])
                    elif "exception" in error:
                        errors.append(error["exception"])

                msg = "{opname}: ".format(opname=opname) + ", ".join(errors)
            else:
                msg = "{opname}: An unexpected error has occurred".format(opname=opname)
            raise ServerError(msg)

    def handle(self, operation, path, params, data, headers, tx_uuid):
        default_headers = {"X-TX-UUID": tx_uuid, "X-TX-LENGTH": None, "X-TX-SIZE": None}
        default_params = {}

        if operation.lower() == "all":
            return self.all("{}/{}".format(self._connection.baseurl, path))
        elif operation.lower() == "create":
            return self.create("{}/{}".format(self._connection.baseurl, path), data)

        # return getattr(self, operation.lower())(
        #     "{}/{}".format(self._connection.baseurl, path), params, headers, data)

    def create(self, path, data, params):
        logger.debug("calling POST (CREATE) on {}".format(path))

        response = self._session.post(
            "{}/{}".format(self._connection.baseurl, path),
            data=json.dumps(data),
            params=params,
        )
        self._check_for_errors(response, 201, "CREATE")

        return response.json()

    def get_or_create(self, path, data, params):
        logger.debug("calling POST (GET_OR_CREATE) on {}".format(path))

        try:
            return self.create(path, data, params)
        except ServerError as e:
            m = re.match(
                r"CREATE: Node\(\d+\) already exists with label `\w+` and property `(?P<attr>\w+)` = '(?P<value>\w+)'",
                str(e),
            )
            if m is not None:
                response, mime_type = self.filter(
                    path, {m.group("attr"): m.group("value")}
                )
                assert len(response) == 1
                return response[0]
            else:
                raise e

    def get(self, path, params):
        logger.debug("calling GET on {}".format(path))

        response = self._session.get(
            "{}/{}".format(self._connection.baseurl, path), params=params
        )
        self._check_for_errors(response, 200, "GET")

        return response.json()

    def all(self, path, params):
        logger.debug("calling GET (ALL) on {}".format(path))

        response = self._session.get(
            "{}/{}".format(self._connection.baseurl, path), params=params
        )
        self._check_for_errors(response, 200, "ALL")

        return (response.json(), response.headers["content-range"])

    def filter(self, path, params):
        logger.debug("calling GET (FILTER) on {}".format(path))

        response = self._session.get(
            "{}/{}".format(self._connection.baseurl, path), params=params
        )
        self._check_for_errors(response, 200, "FILTER")

        return (response.json(), response.headers["content-range"])

    def delete(self, path, params, headers):
        logger.debug("calling DELETE on {}".format(path))

        response = self._session.delete(
            "{}/{}".format(self._connection.baseurl, path),
            params=params,
            headers=headers,
        )
        self._check_for_errors(response, 200, "DELETE")

        return response.json()

    def update(self, path, data, headers):
        logger.debug("calling PUT (UPDATE) on {}".format(path))

        path = "{}/{}".format(self._connection.baseurl, path)
        response = self._session.put(path, data=json.dumps(data), headers=headers)
        self._check_for_errors(response, 200, "UPDATE")

        return (response.json(), response.status_code)

    def upsert(self, path, data, headers):
        logger.debug("calling POST (UPSERT) on {}".format(path))

        path = "{}/{}".format(self._connection.baseurl, path)
        response = self._session.post(path, data=json.dumps(data), headers=headers)
        self._check_for_errors(response, 200, "UPSERT")

        return (response.json(), response.status_code)

    def delsert(self, path, data, headers):
        logger.debug("calling POST (DELSERT) on {}".format(path))

        path = "{}/{}".format(self._connection.baseurl, path)
        response = self._session.post(path, data=json.dumps(data), headers=headers)
        self._check_for_errors(response, 200, "DELSERT")

        return (response.json(), response.status_code)

    def personalise(self, path, params, headers):
        logger.debug("calling PERSONALISE on {}".format(path))

        response = self._session.get(
            "{}/{}".format(self._connection.baseurl, path),
            params=params,
            headers=headers,
        )
        self._check_for_errors(response, 200, "PERSONALISE")

        return response.json()

    def transaction_status(self, path):
        logger.debug("calling GET (TRANSACTION_STATUS) on {}".format(path))

        response = self._session.get("{}/{}".format(self._connection.baseurl, path))
        self._check_for_errors(response, 200, "TRANSACTION_STATUS")

        return (response.json(), response.status_code)
