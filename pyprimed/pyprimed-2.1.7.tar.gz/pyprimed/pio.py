# -*- coding: utf-8 -*-
from pyprimed.const import API_OPERATIONS, API_PATH
from pyprimed.models.base import *
from pyprimed.models.model import Model
from pyprimed.models.signal import Signal
from pyprimed.models.prediction import Prediction
from pyprimed.models.universe import Universe
from pyprimed.models.target import Target
from pyprimed.models.models import Models
from pyprimed.models.universes import Universes
from pyprimed.models.targets import Targets
from pyprimed.models.predictions import Predictions
from pyprimed.models.apikeys import Apikeys
from pyprimed.models.users import Users
from pyprimed.util import Connection
from pyprimed.api import Client
from pyprimed.exceptions import MethodNotAllowedExpection, ConnectionFailedError

import json
import uuid
import logging
import daiquiri
import time

daiquiri.setup(level=logging.INFO)

logger = daiquiri.getLogger(__name__)


class Pio(Resource):
    """
    pyprimed entrypoint.

    ```
    pio = Pio(uri='http://user:password@localhost:5000')
    ```

    # Arguments
    uri (string): PrimedIO connectionstring, defaults to 'http://user:password@localhost:5000'
    version (string): API version, defaults to "1"
    """

    PATH = "/"

    def __init__(self, uri="http://user:password@localhost:5000", version="1"):

        super().__init__(parent=None, uid=None)

        self._uri = uri
        self._version = version

        self._connection = Connection.from_uri(uri, version)
        self._client = Client(self._connection)

        self.apikeys = Apikeys(self, API_PATH["apikeys"], API_OPERATIONS["apikeys"])

        self.models = Models(self, API_PATH["models"], API_OPERATIONS["models"])

        self.universes = Universes(
            self, API_PATH["universes"], API_OPERATIONS["universes"]
        )

        self.targets = Targets(self, API_PATH["targets"], API_OPERATIONS["targets"])

        self.predictions = Predictions(
            self, API_PATH["predictions"], API_OPERATIONS["predictions"]
        )

        self.predictions._bind_using_right("targets", "upsert")

        self.users = Users(self, API_PATH["users"], API_OPERATIONS["users"])

        # pending operations, executed when calling `_dispatch_requests()`
        self._operation_queue = []

    def _rollback(self):
        pass

    def _mark_done(self, resource, guuid):
        path = "/{resource}/mark_done/{guuid}".format(resource=resource, guuid=guuid)

        retries = 5
        c = 0
        err = None
        while c < retries:
            try:
                return self._client._mark_done(path)
            except Exception as e:
                err = e
                c += 1
            time.sleep(1)

        raise ConnectionFailedError("number of retries exceeded: {err}".format(err=err))

    def _dispatch_request(
        self, caller, operation, path, params=None, data=None, headers=None
    ):
        if not caller.is_allowed(operation):
            raise MethodNotAllowedExpection(operation)

        retries = 5
        c = 0
        err = None
        while c < retries:
            try:
                if operation.lower() == "create":
                    return self._client.create(path, data, params)
                elif operation.lower() == "update":
                    return self._client.update(path, data, headers)
                elif operation.lower() == "get":
                    return self._client.get(path, params)
                elif operation.lower() == "all":
                    return self._client.all(path, params)
                elif operation.lower() == "filter":
                    return self._client.filter(path, params)
                elif operation.lower() == "upsert":
                    return self._client.upsert(path, data, headers)
                elif operation.lower() == "delsert":
                    return self._client.delsert(path, data, headers)
                elif operation.lower() == "delete":
                    return self._client.delete(path, params, headers)
                elif operation.lower() == "personalise":
                    return self._client.personalise(path, params, headers)
                elif operation.lower() == "transaction_status":
                    return self._client.transaction_status(path)
                elif operation.lower() == "get_or_create":
                    return self._client.get_or_create(path, data, params)
                break
            except Exception as e:
                err = e
                c += 1
            time.sleep(1)

        raise ConnectionFailedError("number of retries exceeded: {err}".format(err=err))

    def _dispatch_requests(self):
        """Perform the chained operations sequentially. Rollback in
        case of failure.
        """
        failure = False
        _tx_uuid = str(uuid.uuid4())

        while len(self._operation_queue) > 0:
            operation = self._operation_queue.pop()
            result = self._client.handle(*operation, tx_uuid=_tx_uuid)

        if (
            failure
        ):  # TODO, ensure we only rollback when applicable (DELETE rollback makes no sense)
            self._rollback(_tx_uuid)

    def _push_operation(
        self, caller, operation, path, params=None, data=None, headers=None
    ):
        # """Proxy operation through which all operations to the API go

        # :param caller: calling class
        # :type caller: :class: `pyprimed.models.base.Collection`
        # :param operation: any of the following operations: `CREATE`, `ALL`, `UPSERT`, `DELETE`
        # :type operation: string
        # :param path: API path corresponding to the operation
        # :type path: string
        # :param params: additional params, defaults to None
        # :type params: dictionary, optional
        # :param data: payload (applicable only to `CREATE` AND `UPSERT` operations, defaults to None
        # :type data: dictionary, optional
        # :param headers: additional headers, defaults to None
        # :type headers: dictionary, optional
        # :raises: MethodNotAllowedExpection when calling a operation not allowed on that collection
        # """
        if not caller.is_allowed(operation):
            raise MethodNotAllowedExpection()

        self._operation_queue.append((operation, path, params, data, headers))
