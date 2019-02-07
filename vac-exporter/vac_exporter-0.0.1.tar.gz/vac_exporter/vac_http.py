import time
import datetime
import pytz
import yaml

from werkzeug.routing import Map, Rule
from werkzeug.serving import run_simple
from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import InternalServerError
from prometheus_client import CONTENT_TYPE_LATEST, Summary, Counter, generate_latest

from .vac_exporter import collect_vac

class VacExporterApplication(object):

    def __init__(self, section, username, password, ignore_ssl, duration, errors):
        self._section = section
        self._username = username
        self._password = password
        self._ignore_ssl = ignore_ssl
        self._duration = duration
        self._errors = errors

        self._url_map = Map([
            Rule('/', endpoint='index'),
            Rule('/healthz', endpoint='healthz'),
            Rule('/metrics', endpoint='metrics'),
            Rule('/vac', endpoint='vac'),
        ])

        self._args = {
            'vac': ['module', 'target']
        }

        self._views = {
            'healthz': self.on_healthz,
            'index': self.on_index,
            'metrics': self.on_metrics,
            'vac': self.on_vac,
        }

    def on_vac(self, module='default', target='localhost'):
        """
        Request handler for /vac route
        """

        if module in self._section:
            start = time.time()
            output = collect_vac(target, self._username, self._password, self._ignore_ssl)
            response = Response(output)
            response.headers['content-type'] = CONTENT_TYPE_LATEST
            self._duration.labels(module).observe(time.time() - start)
        else:
            response = Response("Module '{0}' not found in config".format(module))
            response.status_code = 400

        return response

    def on_metrics(self):
        """
        Request handler for /metrics route
        """

        response = Response(generate_latest())
        response.headers['content-type'] = CONTENT_TYPE_LATEST

        return response

    def on_index(self):
        """
        Request handler for index route (/).
        """

        response = Response(
            """<html>
            <head><title>VAC Exporter</title></head>
            <body>
            <h1>VAC Exporter</h1>
            <p>Visit <code>/vac?target=1.2.3.4</code> to use.</p>
            </body>
            </html>"""
        )
        response.headers['content-type'] = 'text/html'

        return response

    def on_healthz(self):
        """
        Request handler for healthz route (/healthz)
        """

        response = Response(            
            """<html>
            <body>
            OK
            </body>
            </html>"""
        )
        response.headers['content-type'] = 'text/html'

        return response

    def view(self, endpoint, values, args):
        """
        Werkzeug views mapping method.
        """

        params = dict(values)
        if endpoint in self._args:
            params.update({key: args[key] for key in self._args[endpoint] if key in args})

        try:
            return self._views[endpoint](**params)
        except Exception as error: # pylint: disable=broad-except
            self._errors.labels(args.get('module', 'default')).inc()
            raise InternalServerError(error)

    @Request.application
    def __call__(self, request):
        urls = self._url_map.bind_to_environ(request.environ)
        view_func = lambda endpoint, values: self.view(endpoint, values, request.args)
        return urls.dispatch(view_func, catch_http_exceptions=True)

def log(data, *args):
    """
    Log any message in a uniform format
    """
    print("[{0}] {1}".format(datetime.datetime.utcnow().replace(tzinfo=pytz.utc), data % args))


def start_http_server(section, username, password, ignore_ssl, port, address=''):
    """
    Start an HTTP API server
    """
    duration = Summary(
            'vac_collection_duration_seconds',
            'Duration of collections by the VAC exporter',
            ['module'],
        )
    errors = Counter(
            'vac_request_errors_total',
            'Errors in requests to VAC exporter',
            ['module'],
        )
    
    app = VacExporterApplication(section, username, password, ignore_ssl, duration, errors)
    run_simple(address, port, app, threaded=True)
