""" WSGI middleware for appoptics_apm support

Copyright (C) 2016 by SolarWinds, LLC.
All rights reserved.
"""

from appoptics_apm import util
import sys
import time
from six.moves import urllib
from appoptics_apm.loader import load_inst_modules
import traceback as tb

MODULE_INIT_REPORTED = False


class AppOpticsApmMiddleware(object):
    def __init__(self, app, appoptics_apm_config=None, layer="wsgi", profile=False):
        """
        Install instrumentation for tracing a WSGI app.

        Arguments:
            app - the WSGI app that we're wrapping
            appoptics_apm_config - (optional) dictionary with appoptics_apm configuration parameters:
              - appoptics_apm.tracing_mode: 'always', 'never'
              - appoptics_apm.sample_rate: a number from 0 to 1000000 denoting fraction of requests to trace
            layer - (optional) layer name to use, default is "wsgi"
            profile - (optional) profile entire calls to app (don't use in production)
        """
        if appoptics_apm_config is None:
            appoptics_apm_config = {}

        self.wrapped_app = app
        self.appoptics_apm_config = appoptics_apm_config
        self.layer = layer
        self.profile = profile

        if self.appoptics_apm_config.get('appoptics_apm.tracing_mode'):
            util.config['tracing_mode'] = self.appoptics_apm_config['appoptics_apm.tracing_mode']

        if self.appoptics_apm_config.get('appoptics_apm.reporter_port'):
            util.config['reporter_port'] = self.appoptics_apm_config['appoptics_apm.reporter_port']

        if self.appoptics_apm_config.get('appoptics_apm.sample_rate'):
            util.config['sample_rate'] = float(self.appoptics_apm_config['appoptics_apm.sample_rate'])

        # load pluggable instrumentation
        load_inst_modules()

        # phone home
        global MODULE_INIT_REPORTED
        if not MODULE_INIT_REPORTED:
            util.report_layer_init(layer=layer)
            MODULE_INIT_REPORTED = True

    def __call__(self, environ, start_response):
        xtr_hdr = environ.get("HTTP_X-Trace", environ.get("HTTP_X_TRACE"))
        end_evt = None
        if not util.ready():
            return self.wrapped_app(environ, start_response)

        start_time = time.time() * 1e6
        # start the trace: ctx.is_valid() will be False if not tracing this request
        ctx, start_evt = util.Context.start_trace(self.layer, xtr=xtr_hdr)

        if ctx.is_sampled():
            # get some HTTP details from WSGI vars
            # http://www.wsgi.org/en/latest/definitions.html
            for hosthdr in ("HTTP_HOST", "HTTP_X_HOST", "HTTP_X_FORWARDED_HOST", "SERVER_NAME"):
                if hosthdr in environ:
                    start_evt.add_info("HTTP-Host", environ[hosthdr])
                    break
            if 'PATH_INFO' in environ:
                start_evt.add_info("URL", environ['PATH_INFO'])
            if 'REQUEST_METHOD' in environ:
                start_evt.add_info("Method", environ['REQUEST_METHOD'])
            if 'QUERY_STRING' in environ:
                start_evt.add_info("Query-String", environ['QUERY_STRING'])

            ctx.report(start_evt)
            ctx.set_as_default()
            end_evt = ctx.create_event('exit', self.layer)

        response_body = []

        # Seems I have to use a list for status_str as there is no 'non-local' in Python 2.
        status_str = ['200 OK', ]

        def wrapped_start_response(status, headers, exc_info=None):
            status_str[0] = status

            if ctx.is_sampled():
                end_evt.add_info("Status", status.split(' ', 1)[0])
                if exc_info:
                    _t, exc, trace = exc_info
                    end_evt.add_info("ErrorMsg", str(exc))
                    end_evt.add_info("ErrorClass", exc.__class__.__name__)
                    end_evt.add_info("Backtrace", "".join(tb.format_list(tb.extract_tb(trace))))
                headers.append(("X-Trace", end_evt.id()))
            elif ctx.is_valid():
                headers.append(("X-Trace", str(ctx)))
            start_response(status, headers)
            if self.profile:
                return response_body.append

        stats = None
        result = None
        exc_thrown = False
        domain = None

        try:
            if self.profile and ctx.is_sampled():
                try:
                    # XXX test cProfile and pstats exist
                    import cStringIO, cProfile, pstats
                except ImportError:
                    self.profile = False

            if self.profile and ctx.is_sampled():
                def runapp():
                    appiter = self.wrapped_app(environ, wrapped_start_response)
                    response_body.extend(appiter)
                    if hasattr(appiter, 'close'):
                        appiter.close()

                p = cProfile.Profile()
                p.runcall(runapp)
                body = ''.join(response_body)
                result = [body]

                try:
                    sio = cStringIO.StringIO()
                    s = pstats.Stats(p, stream=sio)
                    s.sort_stats('cumulative')
                    s.print_stats(15)
                    stats = sio.getvalue()
                    sio.close()
                except Exception as aoe:  # catch possible non-application thrown exception
                    util.logger.error('AppOpticsMiddleware cProfile, pstats'
                            'processing encountered problem:: {}'.format(aoe))
            else:
                result = self.wrapped_app(environ, wrapped_start_response)

        except Exception as e:
            exc_thrown = True
            util.logger.error('Error in AppOpticsApmMiddleware: {}'.format(e))
            raise    # re-throw wrapped app raised exception

        finally:
            trans_name = util.get_transaction_name()
            if end_evt:
                # check current TLS context and add to end event if valid
                if util.Context.get_default().is_sampled():
                    end_evt.add_edge(util.Context.get_default())

            #domain and url_tran are required for creating spans
            stats = None if exc_thrown else stats
            setattr(util.Context.transaction_dict, 'status_code', int(status_str[0].split()[0]))
            if util.config['transaction']['prepend_domain_name']:
                domain =environ.get('HTTP_X_FORWARDED_HOST', environ.get('HTTP_HOST'))
            setattr(util.Context.transaction_dict, 'url_tran', None if trans_name else self.get_url(environ))

            setattr(util.Context.transaction_dict, 'http', True)
            setattr(util.Context.transaction_dict, 'domain', domain)
            setattr(util.Context.transaction_dict, 'transaction_name', trans_name)
            setattr(util.Context.transaction_dict, 'start_time', start_time )
            setattr(util.Context.transaction_dict, 'request_method', environ.get('REQUEST_METHOD'))
            self.send_end(ctx, end_evt, environ, threw_error=exc_thrown, stats=stats)

        return result

    def get_url(self, environ):
        """
        Construct the url from environ, see PEP-0333.
        :param environ:
        :return: url
        """
        scheme = environ['wsgi.url_scheme']

        if environ.get('HTTP_HOST'):
            host = environ['HTTP_HOST']
        else:
            host = environ['SERVER_NAME']

        port = ''
        if environ['wsgi.url_scheme'] == 'https':
            if environ['SERVER_PORT'] != '443':
                port = ':{p}'.format(p=environ['SERVER_PORT'])
        else:
            if environ['SERVER_PORT'] != '80':
                port = ':{p}'.format(p=environ['SERVER_PORT'])

        if environ.get('QUERY_STRING'):
            query_string = '?{q}'.format(q=environ['QUERY_STRING'])
        else:
            query_string = ''

        if port in host:
            host_port = host
        else:
            host_port = '{host}{port}'.format(host=host, port=port)

        return '{scheme}://{host_port}{script_name}{path_info}{query_string}'.format(
            scheme=scheme, host_port=host_port,
            script_name=urllib.parse.quote(environ.get('SCRIPT_NAME', '')),
            path_info=urllib.parse.quote(environ.get('PATH_INFO', '')),
            query_string=query_string
        )

    @classmethod
    def send_end(cls, ctx, evt, environ, threw_error=None, stats=None):
        if ctx is None:
            util.logger.warning('ctx is None')
            return

        try:
            if ctx.is_sampled():
                evt.add_edge(ctx)
                util.logger.debug('AppOpticsMiddleware send event: {e}'.format(e = evt))
                if stats:
                    evt.add_info("Profile", stats)
                if threw_error:
                    _t, exc, trace = sys.exc_info()
                    evt.add_info("ErrorMsg", str(exc))
                    evt.add_info("ErrorClass", exc.__class__.__name__)
                    evt.add_info("Backtrace", "".join(tb.format_list(tb.extract_tb(trace))))
                    del trace  # delete reference to traceback object to allow garbage collection

                # gets controller, action
                for k, v in environ.get('wsgiorg.routing_args', [{}, {}])[1].items():
                    if k == "action":
                        evt.add_info(str(k).capitalize(), str(v))
                    elif k == "controller":
                        try:
                            # handle cases used in openstack's WSGI (and possibly others)
                            if v.controller:
                                evt.add_info(str(k).capitalize(), str(v.controller.__class__.__name__))
                            else:
                                evt.add_info(str(k).capitalize(), str(v))
                        except Exception:
                            evt.add_info(str(k).capitalize(), str(v))

        finally:
            # report, then clear trace context now that trace is over. Either ctx is_sampled or not,
            # end_trace must be called to create spans
            ctx.end_trace(evt)
