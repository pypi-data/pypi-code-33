""" AppOptics APM instrumentation API for Python.
When imported, the appoptics_apm_init() function will be executed to do some initialization tasks.

Copyright (C) 2016 by SolarWinds, LLC.
All rights reserved.
"""

import logging
import inspect
import os
import re
import time
import sys
import types
import traceback
from collections import defaultdict
import threading

import six
from decorator import decorator

__version__ = '3.4.8'

# "invalid name ... For type constant"
# pylint interprets all module-level variables as being 'constants'.
# pylint: disable=C0103

# Agent process start time, which is supposed to be a constant. -- don't modify it.
AGENT_START_TIME = time.time() * 1e6

# Constants from liboboe
OBOE_TRACE_NEVER = 0
OBOE_TRACE_ALWAYS = 1
OBOE_TRACE_THROUGH = 2

# oboe modules
OBOE_MODULE_ALL = -1

# Debug level from liboboe: oboe_debug.h
OBOE_DEBUG_DISABLE = -1
OBOE_DEBUG_FATAL = 0
OBOE_DEBUG_ERROR = 1
OBOE_DEBUG_WARNING = 2
OBOE_DEBUG_INFO = 3
OBOE_DEBUG_LOW = 4
OBOE_DEBUG_MEDIUM = 5
OBOE_DEBUG_HIGH = 6

# Map the oboe debug level to python logging level
_logging_map = {
    OBOE_DEBUG_DISABLE: logging.CRITICAL,
    OBOE_DEBUG_FATAL: logging.CRITICAL,
    OBOE_DEBUG_ERROR: logging.ERROR,
    OBOE_DEBUG_WARNING: logging.WARNING,
    OBOE_DEBUG_INFO: logging.INFO,
    OBOE_DEBUG_LOW: logging.DEBUG,
    OBOE_DEBUG_MEDIUM: logging.DEBUG,
    OBOE_DEBUG_HIGH: logging.DEBUG
    }

# Sample rate configuration sources
OBOE_SAMPLE_RATE_SOURCE_FILE = 1
OBOE_SAMPLE_RATE_SOURCE_DEFAULT = 2
OBOE_SAMPLE_RATE_SOURCE_OBOE = 3
OBOE_SAMPLE_RATE_SOURCE_LAST_OBOE = 4
OBOE_SAMPLE_RATE_SOURCE_DEFAULT_MISCONFIGURED = 5
OBOE_SAMPLE_RATE_SOURCE_OBOE_DEFAULT = 6
OBOE_SAMPLE_RATE_SOURCE_CUSTOM = 7

# Masks for bitwise ops
ZERO_MASK = 0b0000000000000000000000000000
SAMPLE_RATE_MASK = 0b0000111111111111111111111111
SAMPLE_SOURCE_MASK = 0b1111000000000000000000000000
ZERO_SAMPLE_RATE_MASK = 0b1111000000000000000000000000
ZERO_SAMPLE_SOURCE_MASK = 0b0000111111111111111111111111

def _apm_str(non_string):
    """converts non-string type to string if possible
       otherwise return as is intact
       * this typically happens python2 unicode string
    """
    try:
        return str(non_string)
    except UnicodeEncodeError as unicode_exception:
        # 'utf-8 encoding is more safe if there is regex processing etc. for
        # consistence encode unicode using utf-8
        logger.debug('converting unicode to string error, string: {non_string}'
                     'message:{message}'.format(
                         non_string=non_string.encode('utf-8'), message=str(unicode_exception)))
        return non_string.encode('utf-8')
    except:
        return non_string

def _get_logger():
    """Define the logger.
    """
    if not (hasattr(logging, 'NullHandler') and callable(logging.NullHandler)):
        class NullHandler(logging.Handler):
            def emit(self, record):
                pass
        logging.NullHandler = NullHandler

    _logger = logging.getLogger(__name__)
    if ('APPOPTICS_DEBUG_LEVEL' in os.environ and
            int(os.environ['APPOPTICS_DEBUG_LEVEL']) == OBOE_DEBUG_DISABLE):
        _logger.addHandler(logging.NullHandler())
        _logger.disabled = True
    else:
        sh = logging.StreamHandler() # get stream handler to custom logging prefix
        f = logging.Formatter('%(asctime)s [ %(name)s %(levelname)-8s] %(message)s')
        sh.setFormatter(f)
        _logger.addHandler(sh)  # use sys.stderr; see oboeware #63
        _logger.setLevel(
            _logging_map[int(os.getenv('APPOPTICS_DEBUG_LEVEL', OBOE_DEBUG_WARNING))])
    return _logger


logger = _get_logger()

def disable_logger(disable=True):
    '''To disable logging, setting logger disabled as True.
       To restoring logging, set disabled as False
    '''
    logger.disabled = disable

reporter_instance = None

# test harness?  If not, check if we will run in no-op on this platform
TEST_MODE = 'APPOPTICS_TEST' in os.environ

if TEST_MODE:
    from appoptics_apm.appoptics_apm_test import (
        Context as SwigContext,
        Event as SwigEvent,
        Reporter,
        Metadata,
        DebugLog,
        Span as SwigSpan,
        CustomMetrics,
        MetricTags,
        )

    logger.error("AppOptics APM Oboe running in APPOPTICS_TEST mode; will not emit reports")
else:
    try:
        from appoptics_apm.swig.oboe import (
            Context as SwigContext,
            Event as SwigEvent,
            Reporter,
            Metadata,
            DebugLog,
            Span as SwigSpan,
            CustomMetrics,
            MetricTags,
            )
    except ImportError as e:
        from appoptics_apm.appoptics_apm_noop import (
            Context as SwigContext,
            Event as SwigEvent,
            Reporter,
            Metadata,
            DebugLog,
            Span as SwigSpan,
            CustomMetrics,
            MetricTags,
            )

        logger.warning("Module native extension lib not found. "
                       "Tracing is disabled and will go into no-op mode. "
                       "Contact support@appoptics.com if this is unexpected. "
                       "ImportError was: {e}".format(e=e))


def custom_metrics_summary(name, value, count=1, host_tag=False, service_name=None, tags=None, tags_count=0):
    """
    Creates a new or adds to an existing Summary Metric.

    :param name:str the name of the metrics, a part of the "metric key"
    :param value:float a value to be recorded associated with this "metric key"
    :param count:int (optional) count of metrics being reported, default is 1
    :param host_tag:boolean (optional) default is False, whether host information should be included
    :param service_name:str (optional) not yet supported, default is None
    :param tags: (optional) appoptics_apm.MetricTags which holds key/value pairs that describe
           the metric and a part of the "metric key", see example below
    :param tags_count: (optional) if tags is given, this must be set to the count of items in tags
    :return: None

    :example::
        # create a MetricTags object for two tags
        tags_count = 2
        tags = appoptics_apm.MetricTags(tags_count)
        # add tags into MetricTags by specifying the index and tag key and value
        tags.add(0, "Peter", "42")
        tags.add(1, "Paul", "45")
        # submit the metric
        appoptics_apm.custom_metrics_summary("my-summary-metric", 13.04, 1, False, None, tags, tags_count)
    """
    # convert None string to empty value, otherwise will cause oboe segfault
    if tags is None:
        tags = MetricTags(0)
        tags_count = 0
    CustomMetrics.summary(name, value, count, host_tag, None, tags, tags_count)


def custom_metrics_increment(name, count, host_tag=False, service_name=None, tags=None, tags_count=0):
    """
    Creates a new or adds to an existing Increment Metric.

    :param name:str the name of the metrics, a part of the "metric key"
    :param count:int increment value, typically 1
    :param host_tag:boolean (optional) default is False, whether host information should be included
    :param service_name:str (optional) not yet supported, default is None
    :param tags: (optional) appoptics_apm.MetricTags which holds key/value pairs that describe
           the metric and a part of the "metric key", see example below
    :param tags_count: (optional) if tags is given, this must be set to the count of items in tags
    :return: None

    :example::
        # create a MetricTags object for two tags
        tags_count = 2
        tags = appoptics_apm.MetricTags(tags_count)
        # add tags into MetricTags by specifying the index and tag key and value
        tags.add(0, "Peter", "42")
        tags.add(1, "Paul", "45")
        # submit the metric
        appoptics_apm.custom_metrics_increment("my-counter-metric", 1, False, None, tags, tags_count)
    """
    if tags is None:
        tags = MetricTags(0)
        tags_count = 0
    CustomMetrics.increment(name, count, host_tag, None, tags, tags_count)


_ready = False

def ready():
    """This function is called by functions outside of this module.
    They should not check the value of _ready directly."""
    global _ready
    return _ready


class AppOpticsApmException(Exception):
    """ AppOptics APM Exception Class """
    pass


class AppOpticsApmConfig(object):
    """ AppOptics APM Configuration Class
    The precedence: Environment Variables > local configurations > default values
    For now liboboe will read the environment variables by itself so we don't need
    to refresh the settings to liboboe space, this applies to collector ip/port and
    service_key, as well as some other configurations."""
    complex_options = ['inst', 'transaction']
    additional_opts = ['sample_rate', 'tracing_mode',]
    delimiter = '.'

    def __init__(self, **kwargs):
        self._config = dict()

        # Update the config with default values
        self._config['service_key'] = '' 
        self._config['hostname_alias'] = ''
        self._config['collector_mode'] = 'ssl'  # ssl, udp
        self._config['enable_sanitize_sql'] = True  # Set to true to strip query literals
        self._config['reporter_host'] = '127.0.0.1'  # Report to localhost by default
        self._config['reporter_port'] = 4444  # hardcoded to 4444
        self._config['warn_deprecated'] = True
        self._config['inst_enabled'] = defaultdict(lambda: True)
        self._config['log_level'] = OBOE_DEBUG_WARNING

        self._config['transaction'] = defaultdict(lambda: True)
        self._config['transaction']['prepend_domain_name'] = False

        # Initialize dictionaries for per instrumentation configuration
        self._config['inst'] = defaultdict(lambda: True)

        self._config['inst']['django_orm'] = defaultdict(lambda: True)
        self._config['inst']['django_orm']['collect_backtraces'] = True

        self._config['inst']['httplib'] = defaultdict(lambda: True)
        self._config['inst']['httplib']['collect_backtraces'] = True

        self._config['inst']['memcache'] = defaultdict(lambda: True)
        self._config['inst']['memcache']['collect_backtraces'] = False

        self._config['inst']['pymongo'] = defaultdict(lambda: True)
        self._config['inst']['pymongo']['collect_backtraces'] = True

        self._config['inst']['redis'] = defaultdict(lambda: True)
        self._config['inst']['redis']['collect_backtraces'] = False

        self._config['inst']['sqlalchemy'] = defaultdict(lambda: True)
        self._config['inst']['sqlalchemy']['collect_backtraces'] = True

        cnf_file = os.environ.get('APPOPTICS_APM_CONFIG_PYTHON', os.environ.get('APPOPTICS_PYCONF', None))
        if cnf_file:
            self.update_with_cnf_file(cnf_file)

        self._config.update(kwargs)
        self.update_with_env_var()
        logger.debug('Intrumention config : {config}'.format(config = self._config))

    def update_with_env_var(self):
        """Update the settings with environment variables."""
        self._config['collector_mode'] = os.environ.get('APPOPTICS_REPORTER', self._config['collector_mode'])
        # We don't need to refresh the log_level for liboboe as it will read the same env variable
        # by itself. See oboe_debug_log_init()@ oboe_debug.c
        self._config['service_key'] = os.environ.get('APPOPTICS_SERVICE_KEY',
                                                     self._config['service_key'])
        self._config['hostname_alias'] = os.environ.get('APPOPTICS_HOSTNAME_ALIAS',
                                                        self._config['hostname_alias'])
        self._config['log_level'] = int(os.environ.get('APPOPTICS_DEBUG_LEVEL', self._config['log_level']))
        self._config['transaction']['prepend_domain_name'] = int(
            os.environ.get('APPOPTICS_APM_PREPEND_DOMAIN_NAME', self._config['transaction']['prepend_domain_name']))

    def update_with_cnf_file(self, cnf_path):
        """Update the settings with the config file, if any."""
        def _convert(value):
            """Convert vals to expected types."""
            value = value.lower()
            if value in ('true', 'false'):
                return True if value == 'true' else False
            try:
                value = float(value)
                return value
            except ValueError:
                return value
        cnf = six.moves.configparser.ConfigParser()
        try:
            if not cnf.read(cnf_path):
                logger.warning('Failed to open the config file: {}.'.format(cnf_path))
                return
        except six.moves.configparser.Error as e:
            logger.warning('Failed to read or parse config file: {e}'.format(e=e))

        allowed_opts = list(self._config.keys()) + self.additional_opts
        try:
            for section in cnf.sections():
                if section == 'main':
                    for key, val in cnf.items(section):
                        if key not in allowed_opts or key in self.complex_options:
                            continue
                        val = _convert(val)
                        # There is no 'sample_rate' and 'tracing_mode' in AppOpticsApmConfig so we cannot enforce
                        # type(self._config[key]) here.
                        self._config[key] = val
                elif section in self.complex_options:
                    for key, val in cnf.items(section):
                        if self.delimiter in key:
                            key, sub_key = key.split(self.delimiter, 1)
                        else:
                            sub_key = None
                        if key not in self._config[section]:
                            continue
                        val = _convert(val)
                        if sub_key and sub_key in self._config[section][key]:
                            self._config[section][key][sub_key] = type(self._config[section][key][sub_key])(val)
                        elif not sub_key:
                            self._config[section][key] = type(self._config[section][key])(val)
                        else:
                            logger.debug('Invalid key: [{s}] {k}.{sk}'.format(s=section, k=key, sk=sub_key))
                else:
                    logger.debug('Invalid section: {s} found in {f}'.format(s=section, f=cnf_path))

        except Exception as e:
            logger.warning('AppOptics APM config error: {e}'.format(e=e))

    def __setitem__(self, key, value):
        """Refresh the configurations in liboboe global struct while user changes settings.
        """
        if key == 'tracing_mode':
            if value == 'never':
                SwigContext.setTracingMode(0)
            elif value == 'always':
                SwigContext.setTracingMode(1)
            else:
                logger.warning('Unsupported trace mode: {mode}'.format(mode=value))
                return

            self._config[key] = value

        elif key == 'sample_rate':
            if not (isinstance(value, (int, float)) and (0 <= value <= 1)):
                logger.warning(
                    'Invalid type or range: {var} in {v_type}'.format(var=value, v_type=type(value))
                )
                return

            self._config[key] = value
            SwigContext.setDefaultSampleRate(int(value * 1e6))

        elif key in ('enable_sanitize_sql', 'warn_deprecated'):
            self._config[key] = value
        else:
            logger.warning('Unsupported AppOptics APM config key: {key}'.format(key=key))

    def __getitem__(self, key):
        return self._config[key]

    def __delitem__(self, key):
        del self._config[key]

    def get(self, key, default=None):
        """ Get the value of key"""
        return self._config.get(key, default)


config = AppOpticsApmConfig()

def sys_is_traceable():
    """Check if the required system environment variables APPOPTICS_SERVICE_KEY
    is set."""
    return bool(config['service_key'])

def appoptics_apm_init():
    """Initialize the instrumentation context:
    1. Load the environment variables.
    2. Create a reporter, either ssl or udp
    3. Get sample configurations from collectors: sample_rate and sample_source"""
    global _ready

    if sys_is_traceable():
        # APPOPTICS_COLLECTOR is fetched by underlying library
        # Unfortunately, this function does not return anything for now.
        oboe_log_level = config['log_level']
        logger.setLevel(_logging_map[oboe_log_level])
        if oboe_log_level == OBOE_DEBUG_DISABLE:
            disable_logger()
        ret = SwigContext.init(config['service_key'], config['hostname_alias'], oboe_log_level)
        if ret in (0, None):
            _ready = True
        else:
            logger.error(
                'Tracing enabled but initialization failed with err code: {ret}.'.format(ret=ret)
                )

    elif TEST_MODE:
        _ready = True
    else:
        logger.error(
            "APPOPTICS_SERVICE_KEY must be specified. Tracing disabled."
            )

"""The AppOptics APM initializer will be executed when this package is imported by user application"""
appoptics_apm_init()

###############################################################################
# Low-level Public API
###############################################################################

def _str_backtrace(backtrace=None):
    """ Return a string representation of an existing or new backtrace """
    if backtrace:
        return "".join(traceback.format_tb(backtrace))
    return "".join(traceback.format_stack()[:-1])


def _collect_backtraces(module_name):
    """ Return the collect backtraces config value for module """
    return config['inst'][module_name]['collect_backtraces']


class Context(object):
    """ A wrapper around the swig Metadata """

    #class scope dict to manage active_instance, transaction_name, and start_time
    #initialize it here (early) in case it is referenced before starting a trace
    transaction_dict = threading.local()
    def __init__(self, md):
        if isinstance(md, six.string_types):
            self._md = Metadata.fromString(md)
        else:
            self._md = md
        self.layer= None

    @property
    def md(self):
        return self._md

    # For interacting with SRv1

    @classmethod
    def set_tracing_mode(cls, mode):
        """ Updates liboboe with the configured tracing_mode """
        SwigContext.setTracingMode(mode)

    @classmethod
    def set_default_sample_rate(cls, rate):
        """ Updates liboboe with the configured sample_rate """
        SwigContext.setDefaultSampleRate(rate)

    # For interacting with the thread-local Context

    @classmethod
    def get_default(cls):
        """Returns the Context currently stored as the thread-local default."""
        return cls(SwigContext)

    def set_as_default(self):
        """Sets this object as the thread-local default Context.
        For now the liboboe does not check the validity of the context, it stores a context even
        the option byte is set to not tracing."""
        # We use is_valid() here as we should allow a context with flags=not tracing to be stored
        # in the context thread local storage.
        if self.is_valid():
            SwigContext.set(self._md)

    @classmethod
    def clear_default(cls):
        """Removes the current thread-local Context."""
        SwigContext.clear()

    @classmethod
    def xtr_is_v2(cls, xtr):
        """Check if the X-Trace ID string is V2"""
        return xtr and xtr[:2] == '2B'  # TODO: change to bitwise operations if more flags are added in future

    # For starting/stopping traces
    @classmethod
    def start_trace(cls, layer, xtr=None, force=False):
        """Returns a Context and a start event.
        Takes sampling into account -- may return an (invalid Context, event) pair.
        """
        Context.transaction_dict = threading.local()
        if sample_request(layer, xtr) or force:
            if cls.xtr_is_v2(xtr):
                xtr = '{ver_task_op}{flag}'.format(ver_task_op=xtr[:-2], flag='01')
                md = Metadata.fromString(xtr)
                evt = md.createEvent()
            else:
                md = Metadata.makeRandom(True)
                evt = SwigEvent.startTrace(md)
        else:
            evt = None
            if cls.xtr_is_v2(xtr):
                xtr = '{ver_task_op}{flag}'.format(ver_task_op=xtr[:-2], flag='00')
                md = Metadata.fromString(xtr)
            else:
                md = Metadata.makeRandom(False)

        if evt:
            event = Event(evt, 'entry', layer)
            sample_rate = getattr(Context.transaction_dict, 'sample_rate', None)
            sample_source = getattr(Context.transaction_dict, 'sample_source', None)
            if sample_source:
                event.add_info(
                    'SampleSource',
                    sample_source
                    )
            else:
                logger.debug("No sample_source attribute found")
            if sample_rate:
                event.add_info('SampleRate', int(sample_rate * 1e6))
            else:
                logger.debug("No sample_rate attribute found")
            event.add_info('Language', 'Python')  # in case we have an unclear layer name
        else:
            event = NullEvent()
        ctx = cls(md)
        ctx.layer= layer
        ctx.set_as_default()
        setattr(Context.transaction_dict, 'start_time', time.time() * 1e6)
        setattr(Context.transaction_dict, 'layer', layer)
        logger.debug('start_trace event : {ev}'.format(ev = event))
        return ctx, event

    def set_transaction_name(self, trans_name = ""):
        """ Set transaction name to this trace instance

           Keyword and  arguments:
               trans_name -- transaction name to tag this trace instance
        """

        if not trans_name:
            logger.warning('Invalid transaction name:{n}'.format( n = _apm_str(trans_name)))
            return False

        trans_name = _apm_str(trans_name)
        if self.is_valid():
            setattr(Context.transaction_dict, 'transaction_name', trans_name)
            return True
        else:
            logger.debug("Transactin name ignored as current execution flow is not monitored by agent")
        return False

    def get_transaction_name(self):
        """ Get transaction name of this trace instance"""

        return getattr(Context.transaction_dict, 'transaction_name', None)

    def end_trace(self, event):  # Reports the last event in a trace
        """Ends this trace, rendering this Context invalid.
           submit inbound metrics and get final transaction name
           update event info with transaction name

           Keyword arguments:
           self -- this context instance
           event -- last trace event
        """
        end_time = time.time() * 1e6
        domain = getattr(Context.transaction_dict, 'domain', None)
        if not config['transaction']['prepend_domain_name']:
            domain = None
        if domain is not None and len(domain.split(":")) > 1:
            port  = domain.split(":")[1]
            if port == "80" or port == "443":
                domain = domain.split(":")[0]
        trans_name = getattr(Context.transaction_dict, 'transaction_name', None)
        http_span = getattr(Context.transaction_dict, 'http', None)
        request_method = getattr(Context.transaction_dict, 'request_method', None)
        status_code = getattr(Context.transaction_dict, 'status_code', None)

        start_time = getattr(Context.transaction_dict, 'start_time', None)
        if start_time is None:
            start_time = end_time
            logger.warning('trace start_time not recorded')
        else:
            start_time = int(start_time)
        url_tran = None if trans_name else getattr(Context.transaction_dict, 'url_tran', None)
        span_time = int(end_time - start_time)

        try:
            if http_span:
                if request_method is None or status_code is None:
                    logger.warning(
                        'http_span request info error request_method : {r}, status_code: {s}'.format(
                            r = request_method, s = status_code))
                if trans_name is None and url_tran is None:
                    logger.warning(
                        'http_span error: transaction_name is None, \
                                use set_transaction_name("transaction_name") to set')
                if status_code is None:
                    status_code = 0
                has_error = bool(status_code > 499)  and bool(status_code < 600)
                trans_name = SwigSpan.createHttpSpan(
                    trans_name, url_tran, domain, span_time, status_code, request_method, has_error)
            else:
                trans_name = SwigSpan.createSpan(trans_name, domain, span_time)
            logger.debug(
                'end_trace create span: http: {http}, transaction_name :{xn}'.format(
                    http = http_span, xn = trans_name))
        except Exception as e:
            logger.error('appoptics_apm::end_trace create SPAN fail: {0}'.format(e))

        logger.debug('end_trace event : {ev}'.format(ev = event))
        # True event is sampled, report it. Otherwise it's NullEvent or None, ignore it.
        if isinstance(event, Event):
            event.add_info('TransactionName', trans_name)
            if http_span:
                event.add_info('Method', request_method)
                event.add_info('HTTP-Host', getattr(Context.transaction_dict, 'domain', None))
                event.add_info('URL', getattr(Context.transaction_dict, 'url_tran', None))
                event.add_info('Status', status_code)
            self.report(event)
        self._md = None
        Context.clear_default()

    def create_event(self, label, layer):
        """Returns an Event associated with this Context."""
        if self.is_sampled():
            return Event(self._md.createEvent(), label, layer)
        return NullEvent()

    def report(self, event):
        """Report this Event.
        -------------------------------------------------------------------------------
        | Please note that we don't need to update the current op_id to the context   |
        | as the liboboe helps to do that in functions: oboe_send_event() -->         |
        | oboe_ids_set_op_id(). There is a risk for now that if the reporter fails to |
        | send the event out, the chain will be broken.                               |
        -------------------------------------------------------------------------------
        """
        if self.is_sampled() and event.is_valid():
            if self._md == SwigContext:
                _reporter().sendReport(event.evt)
            else:
                _reporter().sendReport(event.evt, self._md)
            logger.debug('report event: {e}'.format(e = event))

    def report_status(self, event):
        """Report with postStatus() Thrift API. It's mainly for the __Init message
        A code refactoring may be needed here for the boilerplate code"""
        if self.is_sampled() and event.is_valid():
            if self._md == SwigContext:
                _reporter().sendStatus(event.evt)
            else:
                _reporter().sendStatus(event.evt, self._md)

    def is_valid(self):
        """Returns whether this Context is valid.

        Call this before doing expensive introspection. If this returns False,
        then the context is not valid for moving forward to next step.
        """
        return self._md and self._md.isValid()

    def is_sampled(self):
        """Returns whether this Context is sampled.

        Call this before doing expensive introspection. If this returns False,
        then any event created by this Context will not actually return
        information to AppOptics APM. The decision is made by native extension
        for test mode, it is always FALSE, but it need be True under TEST_MODE
        """
        return self.is_valid() and self._md.isSampled() or TEST_MODE

    def copy(self):
        """Make a clone of this Context."""
        return self.__class__(self._md.toString())

    def __str__(self):
        if self._md:
            return self._md.toString()
        return ''


class Event(object):
    """An Event is a key/value bag that will be reported to the Tracelyzer."""
    def __init__(self, raw_evt, label, layer):
        self._evt = raw_evt
        self._evt.addInfo('Label', label)
        self._evt.addInfo('Layer', layer)

    @property
    def evt(self):
        return self._evt

    def add_edge(self, ctx):
        """Connect an additional Context to this Event.

        All Events are created with an edge pointing to the previous Event. This
        creates an additional edge. This pattern is useful for entry/exit pairs
        in a layer.
        """
        if ctx.md == SwigContext:
            self._evt.addEdge(ctx.md.get())
        else:
            self._evt.addEdge(ctx.md)

    def add_edge_str(self, xtr):
        """Adds an edge to this Event, based on a str(Context).

        Useful for continuing a trace, e.g., from an X-Trace header in a service
        call.
        """
        self._evt.addEdgeStr(xtr)

    def add_info(self, key, value):
        """Add a key/value pair to this event."""
        self._evt.addInfo(key, value)

    def add_backtrace(self, backtrace=None):
        """Add a backtrace to this event.

        If backtrace is None, grab the backtrace from the current stack trace.
        """
        self.add_info('Backtrace', _str_backtrace(backtrace))

    @staticmethod
    def is_valid():
        """Returns whether this event will be reported to the Tracelyzer."""
        return True

    def id(self):
        """Returns a string version of this Event.

        Useful for attaching to output service calls (e.g., an X-Trace request
        header).
        """
        return self._evt.metadataString()


class NullEvent(object):
    """Subclass of event that will not be reported to the Tracelyzer.

    All methods here are no-ops. Checking for this class can be done
    (indirectly) by calling is_valid() on an object.
    """

    def __init__(self):
        pass

    def add_edge(self, event):
        pass

    def add_edge_str(self, op_id):
        pass

    def add_info(self, key, value):
        pass

    def add_backtrace(self, backtrace=None):
        pass

    @staticmethod
    def is_valid():
        return False

    @staticmethod
    def id():
        return ''


###############################################################################
# High-level Public API
###############################################################################

try:
    if six.PY2:
        from cStringIO import StringIO
    else:
        from io import StringIO

    import cProfile
    import pstats
    found_cprofile = True
except ImportError:
    found_cprofile = False


def _get_profile_info(p):
    """Returns a sorted set of stats from a cProfile instance."""
    sio = StringIO()
    s = pstats.Stats(p, stream=sio)
    s.sort_stats('time')
    s.print_stats(15)
    stats = sio.getvalue()
    sio.close()
    return stats

def _update_event(evt, keys=None, store_backtrace=True, backtrace=None, edge_str=None):
    """Add the backtrace and edge to the event
    """
    keys = keys or {}

    if isinstance(keys, dict):
        for k, v in keys.items():
            evt.add_info(k, v)
    else:
        logger.debug('_update_event type of {keys} is : {t}'
            'not dict type'.format(keys = keys, t = type(keys)))


    if store_backtrace:
        evt.add_backtrace(backtrace)

    if edge_str:
        evt.add_edge_str(edge_str)
    return evt

def _sanitize_sql(sql_statement=""):
    """ sanitize sql statement
    """
    # regex only works on str type, if it's python3 bytes, decode it
    # if neither string nor bytes, cast to str type
    # checking python3 bytes
    is_byte_sql = not isinstance(sql_statement, str) and isinstance(sql_statement, bytes)

    if is_byte_sql:
        sql_statement = sql_statement.decode()
    elif not isinstance(sql_statement, str): #non-str, non-bytes type
        sql_statement = _apm_str(sql_statement)

    sql = sql_statement

    #replace '...' "..." with ? and keep '', "" intact
    #replace single quotes
    sql = re.sub(r"(?!'')(?<!')'[^']+'", "?", sql)
    #replace double quotes
    sql = re.sub(r'(?!"")(?<!")"[^"]+"', '?', sql)

    #replace number literals to ?
    sql = re.sub(r'([^a-zA-Z_0-9\.]+)'      #excludes leading field names
                r'([1-9]\d*\.?\d*|0\.\d*|'  #decimal number
                r'0[xX][1-9a-fA-F][0-9a-fA-F]*\.?[0-9a-fA-F]*|0[xX]0\.[0-9a-fA-F]*|' #hex number 
                r'0[1-7][0-7]*\.?[0-7]*|00\.[0-7]*)',  #oct number
                r"\g<1>0", sql)

    if is_byte_sql:
        sql = sql.encode()

    return sql

def _log_event(evt, keys=None, store_backtrace=True, backtrace=None, edge_str=None):
    """Add the backtrace and edge, then send it out to the reporter.
    """

    if isinstance(keys, dict) and 'Query' in keys and config['enable_sanitize_sql']:
        keys['Query'] = _sanitize_sql(keys['Query'])

        if 'QueryArgs' in keys:
            del keys['QueryArgs']

    evt = _update_event(evt, keys, store_backtrace, backtrace, edge_str)
    ctx = Context.get_default()
    ctx.report(evt)


def log(label, layer, keys=None, store_backtrace=True, backtrace=None, edge_str=None):
    """Report a single tracing event.

    :label: 'entry', 'exit', 'info', or 'error'
    :layer: The layer name
    :keys: A optional dictionary of key-value pairs to report.
    :store_backtrace: Whether to report a backtrace. Default: True
    :backtrace: The backtrace to report. Default: this call.
    """
    ctx = Context.get_default()
    if not ctx.is_sampled():
        return
    evt = ctx.create_event(label, layer)
    _log_event(
        evt, keys=keys, store_backtrace=store_backtrace,
        backtrace=backtrace, edge_str=edge_str
    )


def start_trace(layer, xtr=None, keys=None, store_backtrace=True, backtrace=None):
    """Start a new trace, or continue one from an external layer.

    :layer: The layer name of the root of the trace.
    :xtr: The X-Trace ID to continue this trace with.
    :keys: An optional dictionary of key-value pairs to report.
    :store_backtrace: Whether to report a backtrace. Default: True
    :backtrace: The backtrace to report. Default: this call.
    """
    keys = keys or {}
    forced_trace = 'Force' in keys

    ctx, evt = Context.start_trace(layer, xtr=xtr, force=forced_trace)

    if ctx.is_valid():  # Set it to the thread local storage even it's not sampled.
        ctx.set_as_default()

    if ctx.is_sampled():
        _log_event(evt, keys=keys, store_backtrace=store_backtrace, backtrace=backtrace)

    return ctx

def start_http_trace(layer, xtr=None, keys=None, store_backtrace=True, backtrace=None, transaction_name = None):
    """Start a new http trace, or continue one from an external layer.

    :layer: The layer name of the root of the trace.
    :xtr: The X-Trace ID to continue this trace with.
    :keys: An optional dictionary of key-value pairs to report.
    :store_backtrace: Whether to report a backtrace. Default: True
    :backtrace: The backtrace to report. Default: this call.
    """
    ctx = start_trace(layer, xtr, keys, store_backtrace, backtrace)
    if ctx.is_valid() and transaction_name is not None:
        ctx.set_transaction_name(transaction_name)
    return ctx



def end_trace(layer, keys=None, http = False):
    """End a trace, reporting a final event.

    This will end a trace locally. If the X-Trace ID returned here is reported
    externally, other processes can continue this trace.

    :layer: The layer name of the final layer.
    :keys: An optional dictionary of key-value pairs to report.
    :http: A flag indicates http span for True or non for False
    """
    setattr(Context.transaction_dict, 'http', http )
    if not http:
        setattr(Context.transaction_dict, 'domain', None )
        setattr(Context.transaction_dict, 'request_method', None)

    ctx = Context.get_default()
    evt = ctx.create_event('exit', layer)
    logger.debug('end_trace create event: {e}'.format(e = evt))
    if not ctx.is_sampled():
        ctx.end_trace(evt)
        return str(ctx)  # Always return the context id in string format.
    else:
        evt = _update_event(evt, keys=keys, store_backtrace=False)
        ctx_id = last_id()
        ctx.end_trace(evt)

    return ctx_id

def end_http_trace(layer_or_ctx, keys=None):
    """End a trace, reporting a final event.

    This will end a trace locally. If the X-Trace ID returned here is reported
    externally, other processes can continue this trace.

    :layer: The layer name of the final layer.
    :keys: An optional dictionary of key-value pairs to report.
    """
    setattr(Context.transaction_dict, 'http', True)

    if isinstance(layer_or_ctx, str):
        return end_trace(layer_or_ctx, keys, True)
    logger.error("AppOptics APM layer name not str type")
    return end_trace(Context.transaction_dict.get('layer', "unknow"), keys, True)

def set_request_info(host = None, status_code = None, method = None, full_path = None):
    """set or update http span info for current request

      this setting only take effect if currently there is an actve tracing
      instance

      Keywords and parameters:
          host -- request host name
          status_code -- response status code
          method -- request method
          full_path -- full uri
    """

    if status_code is not None:
        setattr(Context.transaction_dict, 'status_code', status_code)
    if method is not None:
        setattr(Context.transaction_dict, 'request_method', method)
    if host is not None:
        setattr(Context.transaction_dict, 'domain', host)
    if full_path is not None:
        setattr(Context.transaction_dict, 'url_tran', full_path)

def log_entry(layer, keys=None, store_backtrace=True, backtrace=None):
    """Report the first event of a new layer.

    :layer: The layer name.
    :keys: An optional dictionary of key-value pairs to report.
    :store_backtrace: Whether to report a backtrace. Default: True
    :backtrace: The backtrace to report. Default: this call.
    """
    ctx = Context.get_default()
    if not ctx.is_sampled():
        return
    evt = ctx.create_event('entry', layer)
    _log_event(evt, keys=keys, store_backtrace=store_backtrace, backtrace=backtrace)


def log_error(err_class, err_msg, store_backtrace=True, backtrace=None):
    """Report an error event.

    :err_class: The class of error to report, e.g., the name of the Exception.
    :err_msg: The specific error that occurred.
    :store_backtrace: Whether to report a backtrace. Default: True
    :backtrace: The backtrace to report. Default: this call.
    """
    ctx = Context.get_default()
    if not ctx.is_sampled():
        return

    layer = getattr(Context.transaction_dict, 'layer', None)
    evt = ctx.create_event('error', layer)
    logger.debug('log_error create event: {e}, for layer:{l}'.format(e = evt, l = layer))
    keys = {
        'Spec': 'error',
        'ErrorClass': err_class,
        'ErrorMsg': err_msg
        }
    _log_event(evt, keys=keys, store_backtrace=store_backtrace, backtrace=backtrace)


def log_exception(msg=None, store_backtrace=True):
    """Report the last thrown exception as an error

    :msg: An optional message, to override err_msg. Defaults to str(Exception).
    :store_backtrace: Whether to store the Exception backtrace.
    """
    typ, val, tb = sys.exc_info()
    try:
        if typ is None:
            logger.debug(
                'log_exception should only be called from an exception context '
                '(e.g., except: block)'
            )
            return

        if msg is None:
            try:
                msg = _apm_str(val)
            except Exception:
                msg = repr(val)

        log_error(typ.__name__, msg,
                  store_backtrace=store_backtrace,
                  backtrace=tb if store_backtrace else None)
    finally:
        del tb  # delete reference to traceback object to allow garbage collection


def log_exit(layer, keys=None, store_backtrace=True, backtrace=None, edge_str=None):
    """Report the last event of the current layer.

    :layer: The layer name.
    :keys: An optional dictionary of key-value pairs to report.
    :store_backtrace: Whether to report a backtrace. Default: True
    :backtrace: The backtrace to report. Default: this call.
    """
    ctx = Context.get_default()
    if not ctx.is_sampled():
        return
    evt = ctx.create_event('exit', layer)
    logger.debug('log_exit create event: {e}'.format(e = evt))
    _log_event(
        evt, keys=keys, store_backtrace=store_backtrace, backtrace=backtrace, edge_str=edge_str
    )

def set_transaction_name(trans_name =""):
    """ Sets a transaction name to the current active trace, the transaction name will
    be reported along with the corresponding trace and metrics.
    This overrides the transaction name provided by out-of-the-box instrumentation.
    If multiple transaction names are set on the same trace, then the last one would be used.
    Take note that transaction name might be truncated with invalid characters replaced.

    Keyword arguments:
    trans_name -- customer defined transaction name
    return -- result of setting, True for success
    """

    ctx = Context.get_default()
    ret = ctx.set_transaction_name(trans_name)
    logger.debug('set_transaction_name:{n} returns  {r}'.format(n = _apm_str(trans_name), r = ret))
    return ret

def get_transaction_name():
    """ Returns the currently set custom transaction name, if any. """

    ctx = Context.get_default()
    return ctx.get_transaction_name()

def last_id():
    """Returns a string representation the last event reported."""
    return str(Context.get_default())


###############################################################################
# Python-specific functions
###############################################################################


def _function_signature(func):
    """Returns a string representation of the function signature of the given func."""
    name = func.__name__
    (args, varargs, keywords, defaults) = inspect.getargspec(func)
    argstrings = []
    if defaults:
        first = len(args) - len(defaults)
        argstrings = args[:first]
        for i in range(first, len(args)):
            d = defaults[i - first]
            if isinstance(d, six.string_types):
                d = "'" + d + "'"
            else:
                d = str(d)
            argstrings.append(args[i] + '=' + d)
    else:
        argstrings = args
    if varargs:
        argstrings.append('*' + varargs)
    if keywords:
        argstrings.append('**' + keywords)
    return name + '(' + ', '.join(argstrings) + ')'


def trace(layer='Python', xtr_hdr=None, kvs=None):
    """ Decorator to begin a new trace on a block of code.  Takes into account
    appoptics_apm.config['tracing_mode'] as well as appoptics_apm.config['sample_rate'], so may
    not always start a trace.

    :layer: layer name to report as
    :xtr_hdr: optional, incoming x-trace header if available
    :kvs: optional, dictionary of additional key/value pairs to report
    """

    def _trace_wrapper(func, *f_args, **f_kwargs):
        start_trace(layer, keys=kvs, xtr=xtr_hdr)
        try:
            res = func(*f_args, **f_kwargs)
        except Exception:
            # log exception and re-raise
            log_exception()
            raise
        finally:
            end_trace(layer)

        return res  # return output of func(*f_args, **f_kwargs)

    _trace_wrapper._appoptics_apm_wrapped = True  # mark our wrapper for protection below

    # instrumentation helper decorator, called to add wrapper at "decorate" time
    def decorate_with_trace(f):
        if getattr(f, '_appoptics_apm_wrapped', False):  # has this function already been wrapped?
            return f  # then pass through
        return decorator(_trace_wrapper, f)  # otherwise wrap function f with wrapper

    return decorate_with_trace


class profile_block(object):
    """A context manager for AppOptics APM profiling a block of code with AppOptics APM lib.

    Reports an error event between entry and exit if an exception is thrown,
    then reraises.

    :profile_name: the profile name to use when reporting.  this should be
        unique to the profiled method.
    :store_backtrace: whether to capture a backtrace or not (False)
    :profile: profile this function with cProfile and report the result
    """

    def __init__(self, profile_name, profile=False, store_backtrace=False):
        self.profile_name = profile_name
        self.use_cprofile = profile
        self.backtrace = store_backtrace
        self.p = None  # possible cProfile.Profile() instance

    def __enter__(self):
        ctx = Context.get_default()
        if not ctx.is_sampled():
            return

        # build entry event
        entry_kvs = {
            'Language': 'python',
            'ProfileName': self.profile_name,
            # XXX We can definitely figure out a way to make these
            # both available and fast.  For now, this is ok.
            'File': '',
            'LineNumber': 0,
            'Module': '',
            'FunctionName': '',
            'Signature': ''
            }
        log('profile_entry', None, keys=entry_kvs, store_backtrace=self.backtrace)

        # begin profiling
        if self.use_cprofile and found_cprofile:
            self.p = cProfile.Profile()
            self.p.enable(subcalls=True)

    def __exit__(self, exc_type, exc_val, exc_tb):
        ctx = Context.get_default()
        if not ctx.is_sampled():
            return

        # end profiling
        stats = None
        if self.use_cprofile and found_cprofile and self.p:
            stats = _get_profile_info(self.p)

        # exception?
        if exc_type:
            log_exception()

        # build exit event
        exit_kvs = {}
        if self.use_cprofile and stats:
            exit_kvs['ProfileStats'] = stats
        exit_kvs['Language'] = 'python'
        exit_kvs['ProfileName'] = self.profile_name

        log('profile_exit', None, keys=exit_kvs, store_backtrace=self.backtrace)


def profile_function(profile_name, store_args=False, store_return=False, store_backtrace=False,
                     profile=False, callback=None, entry_kvs=None):
    """Wrap a method for tracing and profiling with the AppOptics APM library.

    Reports an error event between entry and exit if an exception is thrown,
    then reraises.

    :profile_name: the profile name to use when reporting.  this should be
        unique to the profiled method.
    :store_return: report the return value of this function
    :store_args: report the arguments to this function
    :store_backtrace: whether to capture a backtrace or not (False)
    :profile: profile this function with cProfile and report the result
    :callback: if set, calls this function after the wrapped function returns,
        which examines the function, arguments, and return value, and may add
        more K/V pairs to the dictionary to be reported
    """

    def before(func, f_args, f_kwargs):
        # get filename, line number, etc, and cache in wrapped function to avoid overhead
        def cache(name, value_func):
            try:
                if not hasattr(func, name):
                    setattr(func, name, value_func())
            except Exception:
                setattr(func, name, None)

        cache('_appoptics_apm_file', lambda: inspect.getsourcefile(func))
        cache('_appoptics_apm_line_number', lambda: inspect.getsourcelines(func)[1])
        cache('_appoptics_apm_module', lambda: inspect.getmodule(func).__name__)
        cache('_appoptics_apm_signature', lambda: _function_signature(func))

        keys = {
            'Language': 'python',
            'ProfileName': profile_name,
            'File': getattr(func, '_appoptics_apm_file'),
            'LineNumber': getattr(func, '_appoptics_apm_line_number'),
            'Module': getattr(func, '_appoptics_apm_module'),
            'FunctionName': getattr(func, '__name__'),
            'Signature': getattr(func, '_appoptics_apm_signature')
        }
        return f_args, f_kwargs, keys

    def after(func, f_args, f_kwargs, res):

        kvs = {
            'Language': 'python',
            'ProfileName': profile_name
        }

        if callback:
            user_kvs = callback(func, f_args, f_kwargs, res)
            if user_kvs:
                kvs.update(user_kvs)

        return kvs

    # Do function passed in here expect to be bound (have im_func/im_class)?

    return log_method(
        None, store_return=store_return, store_args=store_args, store_backtrace=store_backtrace,
        before_callback=before, callback=after, profile=profile, entry_kvs=entry_kvs
    )


def log_method(layer, store_return=False, store_args=False, store_backtrace=False,
               before_callback=None, callback=None, profile=False, entry_kvs=None,
               send_entry_event=True, send_exit_event=True, except_send_exit_event=False):
    """Wrap a method for tracing with the AppOptics APM library.

    As opposed to profile_function, this decorator gives the method its own layer

    Reports an error event between entry and exit if an exception is thrown,
    then reraises.

    :layer: the layer to use when reporting. If none, this layer will be a
        profile.
    :store_return: report the return value
    :store_args: report the arguments to this function
    :before_callback: if set, calls this function before the wrapped function is
        called. This function can change the args and kwargs, and can return K/V
        pairs to be reported in the entry event.
    :callback: if set, calls this function after the wrapped function returns,
        which examines the function, arguments, and return value, and may add
        more K/V pairs to the dictionary to be reported
    """
    if not entry_kvs:
        entry_kvs = {}

    # run-time event-reporting function, called at each invocation of func(f_args, f_kwargs)

    def _log_method_wrapper(func, *f_args, **f_kwargs):
        log_exit_event = send_exit_event
        ctx = Context.get_default()
        #ctx should never be None, checking here in case
        if ctx is None or not ctx.is_sampled() or not ready():
            if ctx is None:
                logger.error("util._log_method_wrapper failed to get default context")
            return func(*f_args, **f_kwargs)  # pass through to func right away
        if store_args:
            entry_kvs.update({'args': f_args, 'kwargs': f_kwargs})
        if before_callback:
            before_res = before_callback(func, f_args, f_kwargs)
            if before_res:
                f_args, f_kwargs, extra_entry_kvs = before_res
                entry_kvs.update(extra_entry_kvs)
        if store_backtrace:
            entry_kvs['Backtrace'] = _str_backtrace()
        # is func an instance method?
        if 'im_class' in dir(func):
            entry_kvs['Class'] = func.im_class.__name__

        if send_entry_event:
            # log entry event
            if layer is None:
                log('profile_entry', layer, keys=entry_kvs, store_backtrace=False)
            else:
                log('entry', layer, keys=entry_kvs, store_backtrace=False)

        res = None  # return value of wrapped function
        stats = None  # cProfile statistics, if enabled
        try:
            if profile and found_cprofile:  # use cProfile?
                p = cProfile.Profile()
                res = p.runcall(func, *f_args, **f_kwargs)  # call func via cProfile
                stats = _get_profile_info(p)
            else:  # don't use cProfile, call func directly
                res = func(*f_args, **f_kwargs)
        except Exception:
            # log exception and re-raise
            log_exit_event = log_exit_event or except_send_exit_event
            log_exception()
            raise
        finally:
            # prepare data for reporting exit event
            exit_kvs = {}
            edge_str = None

            # call the callback function, if set, and merge its return
            # values with the exit event's reporting data
            if callback and callable(callback):
                try:
                    cb_ret = callback(func, f_args, f_kwargs, res)
                    # callback can optionally return a 2-tuple, where the
                    # second parameter is an additional edge to add to
                    # the exit event
                    if isinstance(cb_ret, tuple) and len(cb_ret) == 2:
                        cb_ret, edge_str = cb_ret
                    if cb_ret:
                        exit_kvs.update(cb_ret)
                except Exception:
                    # should be no user exceptions here; it's a trace-related callback
                    type_, msg_, bt_ = sys.exc_info()
                    if not TEST_MODE:
                        logger.debug("Non-fatal error in log_method callback: %s, %s, %s"
                                     % (str(type_), msg_, _str_backtrace(bt_)))
                    del bt_

            # (optionally) report return value
            if store_return:
                exit_kvs['ReturnValue'] = _apm_str(res)

            # (optionally) report profiler results
            if profile and stats:
                exit_kvs['ProfileStats'] = stats

            if log_exit_event:
                # log exit event
                if layer is None:
                    log(
                        'profile_exit', layer, keys=exit_kvs,
                        store_backtrace=False, edge_str=edge_str
                        )
                else:
                    log(
                        'exit', layer, keys=exit_kvs,
                        store_backtrace=False, edge_str=edge_str
                        )
        return res  # return output of func(*f_args, **f_kwargs)

    _log_method_wrapper._appoptics_apm_wrapped = True  # mark our wrapper for protection below

    # instrumentation helper decorator, called to add wrapper at "decorate" time
    def decorate_with_log_method(f):
        if getattr(f, '_appoptics_apm_wrapped', False):  # has this function already been wrapped?
            return f  # then pass through
        if hasattr(f, '__func__'):  # Is this a bound method of an object
            f = f.__func__  # then wrap the unbound method
        logger.debug('decorate_with_log_method wraps: {f}'.format(f= f.__name__))
        return decorator(_log_method_wrapper, f)  # otherwise wrap function f with wrapper

    # return decorator function with arguments to log_method() baked in
    return decorate_with_log_method


def _reporter():
    """A reporter has already been initialized by appoptics_apm_init() when appoptics_apm is imported.
    However, when a new child process is forked it needs its own reporter. Inside oboe_init_reporter()
    it will check if the current pid matches the stored one, if not it will create a new reporter."""

    global reporter_instance

    if not reporter_instance:
        config_str = ','.join(
            ('port=%s' % (config.get('reporter_port')),
             'cid=%s' % (config.get('service_key')))
            )
        reporter_instance = Reporter(config['collector_mode'], config_str)

    return reporter_instance


def _Event_addInfo_safe(func):
    def wrapped(*args, **kw):
        try:  # call SWIG-generated Event.addInfo (from swig/oboe.py)
            return func(*args, **kw)
        except NotImplementedError:  # unrecognized type passed to addInfo SWIG binding
            # args: [self, KeyName, Value]
            #1. for python3, bytes type is not instance of six.string_types, but
            # it causes exception
            #2. for python3 bytes type, it cann't be cast to string using
            # str(). It must be decoded, otherwise, it would be like
            # "b'stringcontent'"

            if len(args) == 3 and isinstance(args[1], six.string_types):
                # report this error
                func(args[0], '_Warning', 'Bad type for %s: %s' % (args[1], type(args[2])))
                # last resort: coerce type to string
                if isinstance(args[2], bytes) and not isinstance(args[2], str):
                    #python3 bytes need be decoded to str type
                    return func(args[0], args[1], args[2].decode())
                elif hasattr(args[2], '__str__'):
                    return func(args[0], args[1], str(args[2]))
                else:
                    logger.error("AppOptics APM Oboe wrong value type: cannot update event"
                            "with {key}: {value}".format(key = args[1], value = args[2]))

    return wrapped


def sample_request(layer, xtr):
    """This functions calls the liboboe API to get the sampling decision. A side effect
    is to get the server-side sample_rate and sample_source.
    """
    rv = SwigContext.sampleRequest("", xtr or '')

    # For older binding to liboboe that returns true/false, just return that.
    if rv.__class__ == bool or (rv == 0):
        return rv

    # Newer binding to liboboe returns a bit masked integer with SampleRate and
    # Source embedded
    sample_rate = ((rv & SAMPLE_RATE_MASK) / 1e6)
    sample_source = (rv & SAMPLE_SOURCE_MASK) >> 24
    setattr(Context.transaction_dict, 'sample_rate', sample_rate)
    setattr(Context.transaction_dict, 'sample_source', sample_source)

    return True


###############################################################################
# Backwards compatability
###############################################################################

setattr(SwigEvent, 'addInfo', _Event_addInfo_safe(getattr(SwigEvent, 'addInfo')))


def _old_context_log(cls, layer, label, backtrace=False, **kwargs):
    if config['warn_deprecated']:
        logger.debug(
            'appoptics_apm.Context.log is deprecated. '
            'Please use appoptics_apm.log (and note signature change).')
    log(label, layer, store_backtrace=backtrace, keys=kwargs)


def _old_context_log_error(cls, exception=None, err_class=None, err_msg=None, backtrace=True):
    if config['warn_deprecated']:
        logger.debug(
            'appoptics_apm.Context.log_error is deprecated. '
            'Please use appoptics_apm.log_error (and note signature change).'
        )
    if exception:
        err_class = exception.__class__.__name__
        err_msg = str(exception)
    store_backtrace = False
    tb = None
    if backtrace:
        _, _, tb = sys.exc_info()
        store_backtrace = True
    try:
        return log_error(err_class, err_msg, store_backtrace=store_backtrace, backtrace=tb)
    finally:
        del tb


def _old_context_log_exception(cls, msg=None, exc_info=None, backtrace=True):
    if config['warn_deprecated']:
        logger.debug(
            'appoptics_apm.Context.log_exception is deprecated. '
            'Please use appoptics_apm.log_exception (and note signature change).'
        )
    typ, val, tb = exc_info or sys.exc_info()
    if msg is None:
        try:
            msg = str(val)
        except Exception:
            msg = repr(val)
    try:
        return log_error(typ.__name__, msg, store_backtrace=backtrace, backtrace=tb)
    finally:
        del tb


def _old_context_trace(cls, layer='Python', xtr_hdr=None, kvs=None):
    if config['warn_deprecated']:
        logger.debug(
            'appoptics_apm.Context.trace is deprecated. '
            'Please use appoptics_apm.trace (and note signature change).'
        )
    return trace(layer, xtr_hdr=xtr_hdr, kvs=kvs)


def _old_context_profile_function(
        cls, profile_name, store_args=False, store_return=False,
        store_backtrace=False, profile=False, callback=None, **entry_kvs):
    if config['warn_deprecated']:
        logger.debug(
            'appoptics_apm.Context.trace is deprecated. '
            'Please use appoptics_apm.trace (and note signature change).'
        )
    return profile_function(
        profile_name, store_args=False, store_return=False, store_backtrace=False,
        profile=False, callback=None, entry_kvs=entry_kvs
    )


def _old_context_log_method(cls, layer='Python', store_return=False, store_args=False,
                            callback=None, profile=False, **entry_kvs):
    if config['warn_deprecated']:
        logger.debug(
            'appoptics_apm.Context.log_method is deprecated. '
            'Please use appoptics_apm.log_method (and note signature change).'
        )
    return log_method(layer, store_return=store_return, store_args=store_args,
                      callback=callback, profile=profile, entry_kvs=entry_kvs)


class _old_context_profile_block(profile_block):
    def __init__(self, *args, **kw):
        if config['warn_deprecated']:
            logger.debug(
                'appoptics_apm.Context.profile_block is deprecated. '
                'Please use appoptics_apm.profile_block (and note signature change).'
            )
        super(_old_context_profile_block, self).__init__(*args, **kw)


def _old_context_to_string(cls):
    if config['warn_deprecated']:
        logger.debug(
            'appoptics_apm.Context.toString is deprecated. '
            'Please use str(appoptics_apm.Context.get_default())'
        )
    return str(Context.get_default())


def _old_context_from_string(cls, md_string):
    if config['warn_deprecated']:
        logger.debug('appoptics_apm.Context.fromString is deprecated.')
    c = Context(md_string)
    c.set_as_default()


def _old_context_is_valid(cls):
    if config['warn_deprecated']:
        logger.debug(
            'appoptics_apm.Context.isValid is deprecated. '
            'Please use appoptics_apm.Context.get_default().is_valid()'
        )
    return Context.get_default().is_valid()


setattr(Context, 'log', types.MethodType(_old_context_log, Context))
setattr(Context, 'log_error', types.MethodType(_old_context_log_error, Context))
setattr(Context, 'log_exception', types.MethodType(_old_context_log_exception, Context))
setattr(Context, 'log_method', types.MethodType(_old_context_log_method, Context))
setattr(Context, 'trace', types.MethodType(_old_context_trace, Context))
setattr(Context, 'profile_function', types.MethodType(_old_context_profile_function, Context))
setattr(Context, 'profile_block', _old_context_profile_block)
setattr(Context, 'toString', types.MethodType(_old_context_to_string, Context))
setattr(Context, 'fromString', types.MethodType(_old_context_from_string, Context))
setattr(Context, 'isValid', types.MethodType(_old_context_is_valid, Context))


def report_layer_init(layer='Python', keys=None):
    """ Send a status report with postStatus Thrift API showing the initialization and version of
    this layer's instrumentation.
    """
    if not ready():
        logger.debug('AppOptics APM is not ready, ignoring init message of layer {layer}.'.format(layer=layer))
        return

    ver_keys = dict()
    keys = keys or dict()

    ver_keys['__Init'] = 'True'
    ver_keys['Python.Version'] = sys.version
    ver_keys['Python.AppOptics.Version'] = __version__

    ver_keys['Python.InstallDirectory'] = os.path.dirname(__file__)
    ver_keys['Python.InstallTimestamp'] = os.path.getmtime(__file__)  # in sec since epoch
    ver_keys['Python.LastRestart'] = AGENT_START_TIME  # in usec

    # Don't add Hostname here as liboboe will do it for you.
    # ver_keys['Hostname'] = socket.gethostname()

    if layer.lower() == 'tornado':
        try:
            import tornado
            ver_keys["Python.Tornado.Version"] = sys.modules['tornado'].version
        except ImportError as e:
            logger.warning('Failed to report init event for Tornado: {e}'.format(e=e))
            return

    if layer.lower() == 'django':
        try:
            import django
            ver_keys["Python.Django.Version"] = django.get_version()
        except ImportError as e:
            logger.warning('Failed to report init event for Django: {e}'.format(e=e))
            return

    ver_keys.update(keys)

    ctx = Context(Metadata.makeRandom(True))
    if not ctx.is_valid():
        return
    evt = ctx.create_event('single', layer)

    for k, v in ver_keys.items():
        evt.add_info(k, v)
    ctx.report_status(evt)

# Report an status event after everything is done.
report_layer_init('Python')

class oboe_ready_code(object):
    OBOE_SERVER_RESPONSE_UNKNOWN = (0,"Oboe server : unknown error")
    OBOE_SERVER_RESPONSE_OK = (1,"Oboe server : is ready")
    OBOE_SERVER_RESPONSE_TRY_LATER = (2,"Oboe server : not ready yet, try later")
    OBOE_SERVER_RESPONSE_LIMIT_EXCEEDED = (3,"Oboe server : limit exceeded")
    OBOE_SERVER_RESPONSE_INVALID_API_KEY = (4,"Oboe server : invalid API key")
    OBOE_SERVER_RESPONSE_CONNECT_ERROR = (5,"Oboe server : connection error")

    @classmethod
    def code_values(cls):
        code_pairs = [v for k,v in cls.__dict__.items() if not k.startswith("__")]
        return {p[0]:p[1] for p in code_pairs if isinstance(p, tuple)}

def appoptics_ready(wait_milliseconds = 3000, integer_response = False):
    """
     Wait for AppOptics to be ready to send traces.

     This may be useful in short lived background processes when it is important to capture
     information during the whole time the process is running. Usually AppOptics doesn't block an
     application while it is starting up.

     :param wait_milliseconds:int default 3000, the maximum time to wait in milliseconds
     :param integer_response:int default false, return boolean value, otherwise return integer for
     detail information

     :return: return True for ready, False not ready, integer 1 for ready, others not ready

     :Example:

      if not appoptics_ready(10000):
         Logger.info("AppOptics not ready after 10 seconds, no metrics will be sent")
    """

    rc = SwigContext.isReady(wait_milliseconds)
    if not isinstance(rc, int) or not rc in oboe_ready_code.code_values():
        logger.warning("Unrecognized  return code:{rc}".format(rc = _apm_str(rc)))
    elif rc != oboe_ready_code.OBOE_SERVER_RESPONSE_OK[0]:
        logger.warning(oboe_ready_code.code_values()[rc])

    return  rc if integer_response else rc == oboe_ready_code.OBOE_SERVER_RESPONSE_OK[0]
