# Copyright 2017 Okera Inc.

from __future__ import absolute_import

import okera
import datetime
from functools import wraps
import os
import random
import pytz
import time

import certifi
import urllib3
import xml.dom.minidom

from decimal import Context, Decimal
from collections import OrderedDict
from okera._util import get_logger_and_init_null
from okera._thrift_api import (
    TGetDatabasesParams, TGetRegisteredObjectsParams, TGetTablesParams, TNetworkAddress,
    TPlanRequestParams, TRequestType,
    TExecDDLParams, TExecTaskParams, TFetchParams, TListFilesOp, TListFilesParams,
    TRecordServiceException, TRecordFormat, TTypeId,
    OkeraRecordServicePlanner, RecordServiceWorker)
from okera._thrift_util import (
    create_socket, get_transport, TTransportException, TBinaryProtocol,
    PlannerClient, WorkerClient, KERBEROS_NOT_ENABLED_MSG, SOCKET_READ_ZERO)
from .concurrency import (BaseBackgroundTask,
                          ConcurrencyController,
                          default_max_client_process_count)

_log = get_logger_and_init_null(__name__)

def _rpc(func):
    """ Decorator for retries when making RPCs.

        This can be used from a OkeraContext API call, in which case we're just retrying
        establishing a new connection or a Planner/Worker Connection object, in which
        we need to reconnect and retry the RPC.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if isinstance(self, OkeraContext):
            retries = self.get_retries()
            initial_retry_delay_ms = self.get_initial_retry_delay_ms()
        else:
            retries = self.ctx.get_retries()
            initial_retry_delay_ms = self.ctx.get_initial_retry_delay_ms()
        attempt = 0
        while True:
            try:
                if "test_hook_retry" in dir(self):
                    self.test_hook_retry(func.__name__, retries, attempt)
                return func(self, *args, **kwargs)
            except (TTransportException, IOError) as e:
                if retries == 1:
                    raise e
                attempt += 1
                if attempt == retries:
                    _log.error("All tries failed, raising exception.")
                    raise e
                else:
                    # Exponential delay with jitter
                    delay_ms = random.randint(
                        1, 2**(attempt - 1) * initial_retry_delay_ms)

                    _log.warning(
                        "Attempt failed. Sleeping %dms and then trying again." % delay_ms)
                    time.sleep(delay_ms / 1000)
                    if not isinstance(self, OkeraContext):
                        self._reconnect()
    return wrapper

""" Context for this user session."""
class OkeraContext():
    def __init__(self, application_name, tz=pytz.utc, retries=3,
            initial_retry_delay_ms=2000):
        _log.debug('Creating Okera context')
        self.__auth = None
        self.__service_name = None
        self.__token = None
        self.__host_override = None
        self.__user = None
        self.__name = application_name
        self.__configure()
        self.__tz = tz
        self.__retries = retries
        self.__initial_retry_delay_ms = initial_retry_delay_ms

    def enable_kerberos(self, service_name, host_override=None):
        """Enable kerberos based authentication.

        Parameters
        ----------
        service_name : str
            Authenticate to a particular `okera` service principal. This is typically
            the first part of the 3-part service principal (SERVICE_NAME/HOST@REALM).

        host_override : str, optional
            If set, the HOST portion of the server's service principal. If not set,
            then this is the resolved DNS name of the service being connected to.

        Returns
        -------
        OkeraContext
            Returns this object.
        """

        if not service_name:
            raise ValueError("Service name must be specified.")
        self.__auth = 'GSSAPI'
        self.__service_name = service_name
        self.__host_override = host_override
        self.__user = None
        _log.debug('Enabled kerberos')
        return self

    def enable_token_auth(self, token_str=None, token_file=None):
        """Enables token based authentication.

        Parameters
        ----------
        token_str : str, optional
            Authentication token to use.
        token_file : str, optional
            File containing token to use.

        Returns
        -------
        OkeraContext
            Returns this object.
        """

        if not token_str and not token_file:
            raise ValueError("Must specify token_str or token_file")
        if token_str and token_file:
            raise ValueError("Cannot specify both token_str token_file")

        if token_file:
            with open(os.path.expanduser(token_file), 'r') as t:
                token_str = t.read()
        self.__configure_token(token_str.strip())
        _log.debug('Enabled token auth')
        return self

    def disable_auth(self):
        """ Disables authentication.

        Returns
        -------
        OkeraContext
            Returns this object.
        """
        self.__auth = None
        self.__token = None
        self.__service_name = None
        self.__host_override = None
        self.__user = None
        _log.debug('Disabled auth')
        return self

    def get_auth(self):
        """ Returns the configured auth mechanism. None if no auth is enabled."""
        return self.__auth

    def get_token(self):
        """ Returns the token string. Note that logging this should be done with care."""
        return self.__token

    def get_name(self):
        """ Returns name of this application. This is recorded for diagnostics on
            the server.
        """
        return self.__name

    def _get_user(self):
        """ Returns the user name. This is ignored if authentication is enabled. """
        return self.__user

    def get_timezone(self):
        return self.__tz

    def get_retries(self):
        return self.__retries

    def get_initial_retry_delay_ms(self):
        return self.__initial_retry_delay_ms

    @_rpc
    def connect(self, host='localhost', port=12050, timeout=10):
        """Get a connection to an ODAS cluster. This connects to the planner service.

        Parameters
        ----------
        host : str or list of hostnames
            The hostname for the planner. If a list is specified, picks a planner at
            random.
        port : int, optional
            The port number for the planner. The default is 12050.
        timeout : int, optional
            Connection timeout in seconds. Default is 10 seconds.

        Returns
        -------
        PlannerConnection
            Handle to a connection. Users should call `close()` when done.
        """
        service = self._connect_planner(host, port, timeout)
        planner = PlannerConnection(service, self, host, port, timeout)
        planner.set_application(self.__name)
        return planner

    def _connect_planner(self, host, port, timeout):
        host, port = self.__pick_host(host, port)

        # Convert from user names to underlying transport names
        auth_mechanism = self.__get_auth()

        _log.debug('Connecting to planner %s:%s with %s authentication '
                   'mechanism', host, port, auth_mechanism)
        sock = create_socket(host, port, timeout, False, None)
        transport = None
        try:
            transport = get_transport(sock, host, auth_mechanism, self.__service_name,
                                      None, None, self.__token, self.__host_override)
            transport.open()
            protocol = TBinaryProtocol(transport)
            service = _ThriftService(PlannerClient(OkeraRecordServicePlanner, protocol))
            # Clear timeout after establishing connection. RPCs can take a long time
            # (vs establishing a connection which should be fast).
            sock.set_timeout(None)
            return service
        except (TTransportException, IOError) as e:
            sock.close()
            if transport:
                transport.close()
            self.__handle_transport_exception(e)
            raise e
        except:
            sock.close()
            if transport:
                transport.close()
            raise

    def connect_worker(self, host='localhost', port=13050, timeout=10):
        """Get a connection to ODAS worker.

        Most users should not need to call this API directly.

        Parameters
        ----------
        host : str or list of hostnames
            The hostname for the worker. If a list is specified, picks a worker at
            random.
        port : int, optional
            The port number for the worker. The default is 13050.
        timeout : int, optional
            Connection timeout in seconds. Default is 10 seconds.

        Returns
        -------
        WorkerConnection
            Handle to a worker connection. Users must call `close()` when done.
        """
        return self._connect_worker(host, port, timeout=timeout)

    @_rpc
    def _connect_worker(self, host, port, timeout=10, options=None):
        host, port = self.__pick_host(host, port, options)

        auth_mechanism = self.__get_auth()
        _log.debug('Connecting to worker %s:%s with %s authentication '
                   'mechanism', host, port, auth_mechanism)

        sock = create_socket(host, port, timeout, False, None)
        transport = None
        try:
            transport = get_transport(sock, host, auth_mechanism, self.__service_name,
                                      None, None, self.__token, self.__host_override)
            transport.open()
            protocol = TBinaryProtocol(transport)
            service = _ThriftService(WorkerClient(RecordServiceWorker, protocol))
            worker = WorkerConnection(service, self)
            worker.set_application(self.__name)
            # Clear timeout after establishing connection. RPCs can take a long time
            # (vs establishing a connection which should be fast).
            sock.set_timeout(None)
            return worker
        except (TTransportException, IOError) as e:
            sock.close()
            if transport:
                transport.close()
            self.__handle_transport_exception(e)
            raise e
        except:
            sock.close()
            if transport:
                transport.close()
            raise

    @staticmethod
    def __pick_host(host, port, options=None):
        """
        Returns a host, port from the input. host can be a string or a list of strings.
        If it is a list, a host is picked from the list. If the host string contains the
        port that port is used, otherwise, the port argument is used.
        """
        if not host:
            raise ValueError("host must be specified")

        if isinstance(host, list):
            chosen_host = host[0]
            if isinstance(chosen_host, TNetworkAddress):
                # With this option, we want to pin a host instead of picking a random one.

                if options and 'PIN_HOST' in options:
                    host.sort(key = lambda v: v.hostname)
                    chosen_host = host[0]
                else:
                    chosen_host = random.choice(host)
                host = chosen_host.hostname
                port = chosen_host.port
            elif isinstance(chosen_host, str):
                if options and 'PIN_HOST' in options:
                    host.sort()
                    host = host[0]
                else:
                    host = random.choice(host)
                host = chosen_host
            else:
                raise ValueError("host list must be TNetworkAddress objects or strings.")

        if isinstance(host, str):
            parts = host.split(':')
            if len(parts) == 2:
                host = parts[0]
                port = int(parts[1])
            elif len(parts) == 1:
                host = parts[0]
                if port is None:
                    raise ValueError("port must be specified")
            else:
                raise ValueError("Invalid host: %s " % host)
        else:
            raise ValueError("Invalid host: %s" % host)
        return host, port

    def __configure(self):
        """ Configures the context based on system wide settings"""
        home = os.path.expanduser("~")
        token_file = os.path.join(home, '.cerebro', 'token')
        if os.path.exists(token_file):
            # TODO: we could catch this exception and go on but having this file be
            # messed up here is likely something to fix ASAP.
            with open(token_file, 'r') as t:
                self.__configure_token(t.read().strip())
            _log.info("Configured token auth with token in home directory.")

    def __configure_token(self, token):
        # Valid authentication tokens contain '.' in them, either an Okera token or a JWT
        # token. For API convenience, we use the token value to mean user (plain text)
        # when run against unauthenticated servers.
        if '.' in token:
            self.__token = token
            self.__auth = 'TOKEN'
            self.__service_name = 'cerebro'
            self.__user = None
        else:
            self.__token = None
            self.__auth = None
            self.__user = token
        self.__host_override = None

    def __handle_transport_exception(self, e):
        """ Maps transport layer exceptions to better user facing ones. """
        if self.__auth and e.message == SOCKET_READ_ZERO:
            e.message = "Server did not respond to authentication handshake. " + \
                        "Ensure server has authentication enabled."
        elif not self.__auth and e.message == SOCKET_READ_ZERO:
            e.message = "Client does not have authentication enabled but it appears " + \
                        "the server does. Enable client authentication."
        elif self.__auth == 'GSSAPI' and KERBEROS_NOT_ENABLED_MSG in e.message:
            e.message = "Client is authenticating with kerberos but kerberos is not " + \
                        "enabled on the server."
        raise e

    def __get_auth(self):
        """ Canonicalizes user facing auth names to transport layer ones """
        auth_mechanism = self.__auth
        if not auth_mechanism:
            auth_mechanism = 'NOSASL'
        if auth_mechanism == 'TOKEN':
            auth_mechanism = 'DIGEST-MD5'
        return auth_mechanism

class _ThriftService():
    """ Wrapper around a thrift service client object """
    def __init__(self, thrift_client, retries=3):
        self.client = thrift_client
        self.retries = retries

    def close(self):
        # pylint: disable=protected-access
        _log.debug('close_service: client=%s', self.client)
        self.client._iprot.trans.close()

    def reconnect(self):
        # pylint: disable=protected-access
        _log.debug('reconnect: client=%s', self.client)
        self.client._iprot.trans.close()
        self.client._iprot.trans.open()

class PlannerConnection():
    """A connection to an ODAS planner. """

    def __init__(self, thrift_service, ctx, host, port, timeout):
        self.service = thrift_service
        self.ctx = ctx
        self.host = host
        self.port = port
        self.timeout = timeout
        self.http_pool = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',
                                             ca_certs=certifi.where())
        _log.debug('PlannerConnection(service=%s)', self.service)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Close the session and server connection."""
        _log.debug('Closing Planner connection')
        self.service.close()

    def _reconnect(self):
        _log.debug('Reconnecting to planner...')
        self.close()
        self.service = self.ctx._connect_planner(self.host, self.port, self.timeout)
        _log.debug('Reconnected to planner')

    def _underlying_client(self):
        """ Returns the underlying thrift client. Exposed for internal use. """
        return self.service.client

    @_rpc
    def get_protocol_version(self):
        """Returns the RPC API version of the server."""
        return self.service.client.GetProtocolVersion()

    @_rpc
    def set_application(self, name):
        """Sets the name of this session. Used for logging purposes on the server."""
        self.service.client.SetApplication(name)

    @_rpc
    def ls(self, path):
        """ Lists the files in this directory

        Parameters
        ----------
        path : str
            The path to list.

        Returns
        -------
        list(str)
            List of files located at this path.
        """

        if not path:
            raise ValueError("path must be specified.")

        params = TListFilesParams()
        params.op = TListFilesOp.LIST
        params.object = path
        if self.ctx._get_user():
            params.requesting_user = self.ctx._get_user()
        return self.service.client.ListFiles(params).files

    @_rpc
    def open(self, path, preload_content=True, version=None):
        """ Returns the object at this path as a byte stream

        Parameters
        ----------
        path : str
            The path to the file to open.

        Returns
        -------
        object
            Returns an object that behaves like an opened urllib3 stream.
        """
        if not path:
            raise ValueError("path must be specified.")

        params = TListFilesParams()
        params.op = TListFilesOp.READ
        params.object = path
        params.version_id = version
        if self.ctx._get_user():
            params.requesting_user = self.ctx._get_user()
        try:
            urls = self.service.client.ListFiles(params).files
            if urls and len(urls) != 1:
                raise ValueError(
                    "Unexpected result from server. Expecting at most one url.")
            return self.http_pool.request('GET', urls[0],
                                          preload_content=preload_content)
        except TRecordServiceException as ex:
            if not ex.detail.startswith('AuthorizationException'):
                raise ex
            # This request (for the path) failed with an authorization exception,
            # meaning this user does not have full access to the path. Try to see
            # if this user has access to a table over this path.
            objs = self.get_catalog_objects_at(path, True)
            if not objs or path not in objs:
                raise ex
            for obj in objs[path]:
                if '.' in obj:
                    return OkeraFsStream(self, obj)

            # No object found, raise original exception
            raise ex

    @_rpc
    def cat(self, path, as_utf8=True):
        """ Returns the object at this path as a string

        Parameters
        ----------
        path : str
            The path to the file to read.

        as_utf8 : bool
            If true, convert the returned data as a utf-8 string (instead of binary)

        Returns
        -------
        str
            Returns the contents at the path as a string.
        """

        result = self.open(path)

        if result.status != 200:
            if 'Content-Type' in result.headers:
                if result.headers['Content-Type'] == 'application/xml':
                    msg = result.data.decode('utf-8').replace('\n', '')
                    tree = xml.dom.minidom.parseString(msg).toprettyxml(indent='  ')
                    raise ValueError("Could not read from path: %s\n\n%s" % (path, tree))
            raise ValueError("Could not read from path: %d" % result.status)

        if not result.data:
            if as_utf8:
                return b""
            return ""

        # Check the types to avoid some double serialization
        if isinstance(result.data, str):
            if as_utf8:
                # Both UTF-8
                if result.data.endswith('\n'):
                    return result.data[:-1]
                return result.data
            else:
                if result.data.endswith('\n'):
                    return result.data[:-1].encode('utf-8')
                return result.data.encode('utf-8')

        # Result is binary
        if result.data.endswith(b'\n'):
            if as_utf8:
                return result.data[:-1].decode('utf-8')
            return result.data[:-1]
        if as_utf8:
            return result.data.decode('utf-8')
        else:
            return result.data

    @_rpc
    def get_catalog_objects_at(self, path_prefix, include_views=False):
        """ Returns the objects (databases or datasets) thats registered with this
            prefix path.

        Parameters
        ----------
        path_prefix : str
            The path prefix to look up objects defined with this prefix.

        include_views : bool
            If true, also return views at this path.

        Returns
        -------
        map(str, list(str))
            For each path with a catalog objects, the list of objects located at that
            path. Empty map if there are none.
        """

        if not path_prefix:
            raise ValueError("path_prefix must be specified.")

        params = TGetRegisteredObjectsParams()
        params.prefix_path = path_prefix
        params.include_views = include_views
        if self.ctx._get_user():
            params.requesting_user = self.ctx._get_user()
        return self.service.client.GetRegisteredObjects(params).object_names

    @_rpc
    def list_databases(self):
        """Lists all the databases in the catalog

        Returns
        -------
        list(str)
            List of database names.

        Examples
        --------
        >>> import okera
        >>> ctx = okera.context()
        >>> with ctx.connect(host = 'localhost', port = 12050) as conn:
        ...     dbs = conn.list_databases()
        ...     'okera_sample' in dbs
        True
        """

        request = TGetDatabasesParams()
        if self.ctx._get_user():
            request.requesting_user = self.ctx._get_user()
        result = self.service.client.GetDatabases(request)
        dbs = []
        for db  in result.databases:
            dbs.append(db.name[0])
        return dbs

    @_rpc
    def list_dataset_names(self, db, filter=None):
        """ Returns the names of the datasets in this db

        Parameters
        ----------
        db : str
            Name of database to return datasets in.
        filter : str, optional
            Substring filter on names to of datasets to return.

        Returns
        -------
        list(str)
            List of dataset names.

        Examples
        --------
        >>> import okera
        >>> ctx = okera.context()
        >>> with ctx.connect(host = 'localhost', port = 12050) as conn:
        ...     datasets = conn.list_dataset_names('okera_sample')
        ...     datasets
        ['okera_sample.sample', 'okera_sample.users', 'okera_sample.users_ccn_masked', 'okera_sample.whoami']
        """
        request = TGetTablesParams()
        request.database = [db]
        request.filter = filter
        if self.ctx._get_user():
            request.requesting_user = self.ctx._get_user()
        tables = self.service.client.GetTables(request).tables
        result = []
        for t in tables:
            result.append(db + '.' + t.name)
        return result

    @_rpc
    def list_datasets(self, db, filter=None):
        """ Returns the datasets in this db

        Parameters
        ----------
        db : str
            Name of database to return datasets in.
        filter : str, optional
            Substring filter on names to of datasets to return.

        Returns
        -------
        obj
            Thrift dataset objects.
        Note
        -------
        This API is subject to change and the returned object may not be backwards
        compatible.
        """

        request = TGetTablesParams()
        request.database = [db]
        request.filter = filter
        if self.ctx._get_user():
            request.requesting_user = self.ctx._get_user()
        tables = self.service.client.GetTables(request)
        return tables

    @_rpc
    def plan(self, request, max_task_count=None, requesting_user=None):
        """ Plans the request to read from CDAS
        Parameters
        ----------
        request : str, required
            Name of dataset or SQL statement to plan scan for.
        requesting_user : str, optional
            Name of user to request plan for, if different from
            the current user.

        Returns
        -------
        object
            Thrift serialized plan object.

        Note
        -------
        This API is subject to change and the returned object may not be backwards
        compatible.
        """

        if not request:
            raise ValueError("request must be specified.")

        params = TPlanRequestParams()
        params.request_type = TRequestType.Sql
        if max_task_count:
            params.max_tasks = max_task_count
        if requesting_user:
            params.requesting_user = requesting_user
        elif self.ctx._get_user():
            params.requesting_user = self.ctx._get_user()

        request = request.strip()
        if request.lower().startswith('select '):
            _log.debug('Planning request for query: %s', request)
            params.sql_stmt = request
        else:
            _log.debug('Planning request to read dataset: %s', request)
            params.sql_stmt = "SELECT * FROM " + request
        plan = self.service.client.PlanRequest(params)
        _log.debug('Plan complete. Number of tasks: %d', len(plan.tasks))
        return plan

    @_rpc
    def execute_ddl(self, sql):
        # pylint: disable=line-too-long
        """ Execute a DDL statement against the server.

        Parameters
        ----------
        sql : str
            DDL statement to run

        Returns
        -------
        list(list(str))
            Returns the result as a table.

        Examples
        --------
        >>> import okera
        >>> ctx = okera.context()
        >>> with ctx.connect(host = 'localhost', port = 12050) as conn:
        ...     result = conn.execute_ddl('describe okera_sample.users')
        ...     result
        [['uid', 'string', 'Unique user id'], ['dob', 'string', 'Formatted as DD-month-YY'], ['gender', 'string', ''], ['ccn', 'string', 'Sensitive data, should not be accessible without masking.']]
        """
        # pylint: enable=line-too-long

        if not sql:
            raise ValueError("Must specify sql string to execute_ddl")
        request = TExecDDLParams()
        request.ddl = sql
        if self.ctx._get_user():
            request.requesting_user = self.ctx._get_user()
        response = self.service.client.ExecuteDDL2(request)
        return response.tabular_result

    @_rpc
    def execute_ddl_table_output(self, sql):
        """ Execute a DDL statement against the server.

        Parameters
        ----------
        sql : str
            DDL statement to run

        Returns
        -------
        PrettyTable
            Returns the result as a table object.

        Examples
        --------
        >>> import okera
        >>> ctx = okera.context()
        >>> with ctx.connect(host = 'localhost', port = 12050) as conn:
        ...     result = conn.execute_ddl_table_output('describe okera_sample.users')
        ...     print(result)
        +--------+--------+-----------------------------------------------------------+
        |  name  |  type  |                          comment                          |
        +--------+--------+-----------------------------------------------------------+
        |  uid   | string |                       Unique user id                      |
        |  dob   | string |                  Formatted as DD-month-YY                 |
        | gender | string |                                                           |
        |  ccn   | string | Sensitive data, should not be accessible without masking. |
        +--------+--------+-----------------------------------------------------------+
        """
        from prettytable import PrettyTable

        if not sql:
            raise ValueError("Must specify sql string to execute_ddl")
        request = TExecDDLParams()
        request.ddl = sql
        if self.ctx._get_user():
            request.requesting_user = self.ctx._get_user()
        response = self.service.client.ExecuteDDL2(request)
        if not response.col_names:
            return None

        t = PrettyTable(response.col_names)
        for row in response.tabular_result:
            t.add_row(row)
        return t

    def scan_as_pandas(self,
                       request,
                       max_records=None,
                       max_client_process_count=default_max_client_process_count(),
                       max_task_count=None,
                       requesting_user=None,
                       options=None,
                       ignore_errors=False,
                       warnings=None,
                       strings_as_utf8=False):
        """Scans data, returning the result for pandas.

        Parameters
        ----------
        request : string, required
            Name of dataset or SQL statement to scan.
        max_records : int, optional
            Maximum number of records to return. Default is unlimited.
        options : dictionary, optional
            Optional key/value configs to specify to the request. Note that these
            options are not guaranteed to be backwards compatible.
        warnings : list(string), optional
            If not None, will be populated with any warnings generated for request.

        Returns
        -------
        pandas DataFrame
            Data returned as a pandas DataFrame object

        Examples
        --------
        >>> import okera
        >>> ctx = okera.context()
        >>> with ctx.connect(host = 'localhost', port = 12050) as conn:
        ...     pd = conn.scan_as_pandas('select * from okera_sample.sample')
        ...     print(pd)
                                       record
        0      b'This is a sample test file.'
        1  b'It should consist of two lines.'
        """
        import pandas
        plan = self.plan(request,
                         max_task_count=max_task_count,
                         requesting_user=requesting_user)
        self._ensure_serialization_support(plan)

        # Return any warnings if the user is interested
        if warnings is not None and plan.warnings:
            for warning in plan.warnings:
                warnings.append(warning.message)

        concurrency_ctl = self._get_concurrency_controller_for_plan(
            plan, max_client_process_count)

        for task in plan.tasks:
            _log.debug('Executing task %s', str(task.task_id))
            concurrency_ctl.enqueueTask(PandasScanTask(self.ctx,
                                                       plan.hosts,
                                                       task,
                                                       max_records,
                                                       options,
                                                       strings_as_utf8))

        result_list = self._start_and_wait_for_results(concurrency_ctl,
                                                       len(plan.tasks),
                                                       limit=max_records,
                                                       is_pandas=True,
                                                       ignore_errors=ignore_errors)
        if not result_list:
            col_names = []
            for col in plan.schema.cols:
                col_names.append(col.name)
            return pandas.DataFrame(columns=col_names)
        else:
            return pandas.concat(result_list).head(max_records)

    def scan_as_json(self,
                     request,
                     max_records=None,
                     warnings=None,
                     max_client_process_count=default_max_client_process_count(),
                     max_task_count=None,
                     requesting_user=None,
                     ignore_errors=False):
        # pylint: disable=line-too-long
        """Scans data, returning the result in json format.

        Parameters
        ----------
        request : string, required
            Name of dataset or SQL statement to scan.
        max_records : int, optional
            Maximum number of records to return. Default is unlimited.
        warnings : list(string), optional
            If not None, will be populated with any warnings generated for request.

        Returns
        -------
        list(obj)
            Data returned as a list of JSON objects

        Examples
        --------
        >>> import okera
        >>> ctx = okera.context()
        >>> with ctx.connect(host = 'localhost', port = 12050) as conn:
        ...     data = conn.scan_as_json('okera_sample.sample')
        ...     data
        [{'record': 'This is a sample test file.'}, {'record': 'It should consist of two lines.'}]
        """
        # pylint: enable=line-too-long

        plan = self.plan(request,
                         max_task_count=max_task_count,
                         requesting_user=requesting_user)
        self._ensure_serialization_support(plan)

        concurrency_ctl = self._get_concurrency_controller_for_plan(
            plan, max_client_process_count)

        # Return any warnings if the user is interested
        if warnings is not None and plan.warnings:
            for warning in plan.warnings:
                warnings.append(warning.message)

        if len(plan.tasks) <= 0:
            return []

        for task in plan.tasks:
            _log.debug('Executing task %s', str(task.task_id))
            concurrency_ctl.enqueueTask(JsonScanTask(self.ctx,
                                                    plan.hosts,
                                                    task,
                                                    max_records))

        res = self._start_and_wait_for_results(concurrency_ctl,
                                               len(plan.tasks),
                                               limit=max_records,
                                               ignore_errors=ignore_errors)
        if max_records is not None:
            return res[:max_records]
        return res

    @staticmethod
    def _get_concurrency_controller_for_plan(plan, max_client_process_count):
        worker_count = min(max_client_process_count, len(plan.tasks))
        return ConcurrencyController(worker_count=worker_count)

    @staticmethod
    def _calculate_limit(current_limit, results, is_pandas):
        if current_limit is None:
            return None
        if is_pandas:
            if len(results) == 0:
                return current_limit
            return max(current_limit-len(results[0].index), 0)
        return max(current_limit-len(results), 0)

    @staticmethod
    def _start_and_wait_for_results(concurrency_ctl,
                                    task_count,
                                    limit=None,
                                    is_pandas=False,
                                    ignore_errors=False):
        results = []
        if not task_count:
            return results
        try:
            task_result_count = 0
            is_completed = False
            # We're setting the limit value into a shared dict that is handed
            # to all async tasks.  The main thread (this function) is responsible
            # for updating the value as records are received.  The async tasks
            # will read this `limit` value from the dict and pass it as the
            # `max_records` param to the worker.  As records are received in the
            # main thread, the `limit` value will decrease until it is zero, at
            # which point the remaining async tasks will immediately return
            # with empty results.
            concurrency_ctl.metrics_dict['limit'] = limit

            # All default values need to be set prior to calling start().  This is
            # because there will be a delay when setting any shared value between
            # processes because the values are cached in each process.
            concurrency_ctl.start()

            while not is_completed:
                res = concurrency_ctl.output_queue.get()
                if res is not None:
                    task_result_count += 1
                    limit = PlannerConnection._calculate_limit(limit, res, is_pandas)
                    results.extend(res)
                    if task_result_count == task_count:
                        is_completed = True
                    concurrency_ctl.metrics_dict['limit'] = limit

            if not ignore_errors and concurrency_ctl.errors_queue.qsize():
                print('One or more errors occurred while processing this query:')
                while concurrency_ctl.errors_queue.qsize():
                    err = concurrency_ctl.errors_queue.get()
                    print('{0}'.format(err))
                    raise err
        finally:
            concurrency_ctl.stop()

        return results

    @staticmethod
    def _ensure_serialization_support(plan):
        if not plan.supported_result_formats or \
                TRecordFormat.ColumnarNumPy not in plan.supported_result_formats:
            raise IOError("PyOkera requires the server to support the " +
                          "`ColumnarNumPy` serialization format. Please upgrade the " +
                          "server to at least 0.8.1.")

class WorkerConnection():
    """A connection to a CDAS worker. """

    def __init__(self, thrift_service, ctx):
        self.service = thrift_service
        self.ctx = ctx
        _log.debug('WorkerConnection(service=%s)', self.service)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Close the session and server connection."""
        _log.debug('Closing Worker connection')
        self.service.close()

    def _reconnect(self):
        self.service.reconnect()

    def get_protocol_version(self):
        """Returns the RPC API version of the server."""
        return self.service.client.GetProtocolVersion()

    def set_application(self, name):
        """Sets the name of this session. Used for logging purposes on the server."""
        self.service.client.SetApplication(name)

    def exec_task(self, task, max_records=None):
        """ Executes a task to begin scanning records.

        Parameters
        ----------
        task : obj
            Description of task. This is the result from the planner's plan() call.
        max_records: int, optional
            Maximum number of records to return for this task. Default is unlimited.

        Returns
        -------
        object
            Handle for this task. Used in subsequent API calls.
        object
            Schema for records returned from this task.
        """
        request = TExecTaskParams()
        request.task = task.task
        request.limit = max_records
        request.fetch_size = 20000
        request.record_format = TRecordFormat.ColumnarNumPy
        result = self.service.client.ExecTask(request)
        return result.handle, result.schema

    def close_task(self, handle):
        """ Closes the task. """
        self.service.client.CloseTask(handle)

    def fetch(self, handle):
        """ Fetch the next batch of records for this task. """
        request = TFetchParams()
        request.handle = handle
        return self.service.client.Fetch(request)

def _columnar_batch_to_python(schema, columnar_records, num_records,
                              ctx_tz=pytz.utc, strings_as_utf8=False):
    # Issues with numpy, thrift and this function being perf optimized
    # pylint: disable=no-member
    # pylint: disable=protected-access
    # pylint: disable=too-many-locals
    import numpy
    cols = columnar_records.cols

    # Things we will return.
    col_names = []
    # Checks if any of the values in this batch are null. Handling NULL can be
    # noticeably slower, so skip it in bulk if possible.
    any_nulls = []
    is_nulls = [None] * len(cols)
    data = [None] * len(cols)

    # For each column seen, the index to append to it. Empty means nothing to append.
    # The planner does not need to generate unique column names in all cases. e.g.
    # 'select c1, c1 from t' will generate two columns called 'c1'. We need to dedup
    # here as we put the columns in a dictionary.
    # In this case we will name the second "c1_2"
    col_names_dedup = {}

    # Go over each column and convert the binary data to python objects. This is very
    # perf sensitive.
    for col in range(0, len(cols)):
        buf = cols[col].data
        if isinstance(buf, str):
            buf = buf.encode()

        name = schema.cols[col].name
        if name not in col_names_dedup:
            col_names_dedup[name] = 2
        else:
            # Keep resolving to dedup
            while name in col_names_dedup:
                idx = col_names_dedup[name]
                col_names_dedup[name] = idx + 1
                name += '_' + str(idx)

        col_names.append(name)
        is_null = numpy.frombuffer(cols[col].is_null.encode(), dtype=numpy.bool)
        any_nulls.append(numpy.any(is_null))
        is_nulls[col] = is_null

        t = schema.cols[col].type.type_id
        if t == TTypeId.STRING or t == TTypeId.VARCHAR:
            off = 4 * num_records
            column = [numpy.nan] * num_records
            lens = numpy.frombuffer(buf[0: off], dtype=numpy.int32)
            if any_nulls[col]:
                for i in range(0, num_records):
                    if not is_null[i]:
                        length = lens[i]
                        column[i] = buf[off:off + length]
                        if strings_as_utf8:
                            column[i] = column[i].decode('utf-8')
                        off += length
            else:
                for i in range(0, num_records):
                    length = lens[i]
                    column[i] = buf[off:off + length]
                    if strings_as_utf8:
                        column[i] = column[i].decode('utf-8')
                    off += length
            if strings_as_utf8:
                data[col] = column
            else:
                data[col] = numpy.array(column, dtype=object)
        elif t == TTypeId.CHAR:
            off = 0
            column = [numpy.nan] * num_records
            length = schema.cols[col].type.len
            if any_nulls[col]:
                for i in range(0, num_records):
                    if not is_null[i]:
                        column[i] = buf[off:off + length]
                        off += length
            else:
                for i in range(0, num_records):
                    column[i] = buf[off:off + length]
                    off += length
            if strings_as_utf8:
                data[col] = ''.join(column)
            else:
                data[col] = numpy.array(column, dtype=object)
        elif t == TTypeId.BOOLEAN:
            data[col] = numpy.frombuffer(buf, dtype=numpy.bool)
        elif t == TTypeId.TINYINT:
            data[col] = numpy.frombuffer(buf, dtype=numpy.int8)
        elif t == TTypeId.SMALLINT:
            data[col] = numpy.frombuffer(buf, dtype=numpy.int16)
        elif t == TTypeId.INT:
            data[col] = numpy.frombuffer(buf, dtype=numpy.int32)
        elif t == TTypeId.BIGINT:
            data[col] = numpy.frombuffer(buf, dtype=numpy.int64)
        elif t == TTypeId.FLOAT:
            data[col] = numpy.frombuffer(buf, dtype=numpy.float32)
        elif t == TTypeId.DOUBLE:
            data[col] = numpy.frombuffer(buf, dtype=numpy.float64)
        elif t == TTypeId.TIMESTAMP_NANOS:
            dt = numpy.dtype([('millis', numpy.int64), ('nanos', numpy.int32)])
            values = numpy.frombuffer(buf, dtype=dt)
            millis = values['millis']
            column = [numpy.nan] * num_records
            for i in range(0, num_records):
                if not is_null[i]:
                    # TODO: use nanos?
                    column[i] = datetime.datetime.fromtimestamp(millis[i] / 1000.0,
                                                                ctx_tz)
            data[col] = column
        elif t == TTypeId.DECIMAL:
            column = [numpy.nan] * num_records
            scale = -schema.cols[col].type.scale
            if schema.cols[col].type.precision <= 18:
              if schema.cols[col].type.precision <= 9:
                  values = numpy.frombuffer(buf, dtype=numpy.int32)
              elif schema.cols[col].type.precision <= 18:
                  values = numpy.frombuffer(buf, dtype=numpy.int64)
              for i in range(0, num_records):
                  if not is_null[i]:
                      column[i] = Decimal(int(values[i])).scaleb(scale)
            else:
                # These decimals are stored as up to 128 bits with two longs back
                # to back. This needs to be reconstructed and we want to compute:
                #   v = longs[i*2+1] << 64 + longs[i*2]
                # This is done carefully to avoid overflow.
                ctx = Context(schema.cols[col].type.precision)
                multiple = ctx.power(2, 64)
                longs = numpy.frombuffer(buf, dtype=numpy.int64)
                for i in range(0, num_records):
                    if is_null[i]:
                        continue
                    v = Decimal(int(longs[i * 2 + 1])) * multiple + longs[i * 2]
                    column[i] = v.scaleb(scale)
            data[col] = column
        else:
            raise RuntimeError("Unsupported type: " + TTypeId._VALUES_TO_NAMES[t])
    return col_names, data, any_nulls, is_nulls

def context(application_name=None):
    """ Gets the top level context object to use pyokera.

    Parameters
    ----------
    application_name : str, optional
        Name of this application. Used for logging and diagnostics.

    Returns
    -------
    OkeraContext
        Context object.

    Examples
    --------
    >>> import okera
    >>> ctx = okera.context()
    >>> ctx                                         # doctest: +ELLIPSIS
    <okera.odas.OkeraContext object at 0x...>
    """
    if not application_name:
        application_name = 'pyokera (%s)' % version()
    return OkeraContext(application_name)

def version():
    """ Returns version string of this library. """
    from . import __version__
    return __version__

class ScanTask(BaseBackgroundTask):
  def __init__(self, name, ctx, plan_hosts, task, max_records, options):
    BaseBackgroundTask.__init__(self, "ScanTask.{0}".format(name))
    self.ctx = ctx
    self.plan_hosts = plan_hosts
    self.task = task
    self.max_records = max_records
    self.options = options
    self.errors = []

  def __call__(self):
    results = []
    total = 0
    if self.max_records is not None and self.max_records <= 0:
        return results
    with self.ctx._connect_worker(self.plan_hosts, None, options=self.options) as worker:
        try:
            handle, schema = worker.exec_task(self.task, self.max_records)
            while True:
                fetch_result = worker.fetch(handle)
                assert fetch_result.record_format == TRecordFormat.ColumnarNumPy
                if fetch_result.num_records:
                    t_results = self.deserialize(schema,
                                                 fetch_result.columnar_records,
                                                 fetch_result.num_records)
                    if t_results:
                        results.extend(t_results)

                    total += fetch_result.num_records

                if fetch_result.done or (self.max_records and total >= self.max_records):
                    break
        except Exception as ex:
            self.errors.append(ex)
        finally:
            worker.close_task(handle)
    return results

  def deserialize(self, schema, columnar_records, num_records):
    '''Abstract definition to deserialize the returned dataset'''
    raise Exception('Invalid invocation of an abstract function: ' +
                    'BaseBackgroundTask::deserialize')

class JsonScanTask(ScanTask):
  def __init__(self, ctx, plan_hosts, task, max_records):
    ScanTask.__init__(self, "JsonScanTask", ctx, plan_hosts, task, max_records, None)

  def deserialize(self, schema, columnar_records, num_records):
    col_names, data, _, is_nulls = _columnar_batch_to_python(
        schema, columnar_records, num_records, self.ctx.get_timezone())
    num_cols = len(col_names)
    result = []
    # Go over each row and construct a python array as a row
    for r in range(0, num_records):
        row = [None] * num_cols
        for c in range(0, num_cols):
            if not is_nulls[c][r]:
                datum = data[c][r]
                row[c] = datum.decode('utf-8') if isinstance(datum, bytes) else datum
        result.append(dict(zip(col_names, row)))
    return result

class PandasScanTask(ScanTask):
  def __init__(self, ctx, plan_hosts, task, max_records, options, strings_as_utf8):
    ScanTask.__init__(self, "PandasScanTask", ctx, plan_hosts, task, max_records, options)
    self.__strings_as_utf8 = strings_as_utf8

  def deserialize(self, schema, columnar_records, num_records):
    import numpy
    import pandas
    result = []
    col_names, data, any_nulls, is_nulls = _columnar_batch_to_python(
        schema, columnar_records, num_records, self.ctx.get_timezone(),
        self.__strings_as_utf8)
    df = pandas.DataFrame(OrderedDict(zip(col_names, data)))
    if len(df):
        for c in range(0, len(col_names)):
            if not any_nulls[c] or df[col_names[c]].dtype == 'object':
                # Either no nulls, or objects are already handled.
                continue
            if isinstance(df[col_names[c]][0], str):
                continue
            # Fix up nulls, replace with nan
            # TODO: this is not the cheapest
            df[col_names[c]] = df[col_names[c]].where(~is_nulls[c], other=numpy.nan)
    result.append(df)
    return result

class OkeraFsStream():
    """ Wrapper object which behaves like a stream to send serialized results back
        in a byte stream based API. The API is intended to be compatible with a
        urllib stream object. """

    def __init__(self, planner, tbl, delimiter=',', quote_strings=True):
        # TODO: this needs to stream the result instead of all at once
        self.planner = planner
        self.tbl = tbl
        self.status = 200
        self.headers = {}
        self.data = planner.scan_as_pandas(
            tbl, max_task_count=1,strings_as_utf8=True).to_csv(
                None, header=True, index=False)

    def read(self, amt):
        return self.data.encode('utf-8')

Binary = memoryview
