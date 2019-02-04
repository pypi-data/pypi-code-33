from pathlib import Path
import ssl

from gevent import pywsgi, spawn
from geventwebsocket.handler import WebSocketHandler

from . import app, settings, mqtt, lan_mode

ssl_kwargs = {
    'certfile': (Path(__file__).parent / 'ssl' / 'server.crt').absolute(),
    'keyfile': (Path(__file__).parent / 'ssl' / 'server.key').absolute(),
}


class Server(pywsgi.WSGIServer):
    def wrap_socket_and_handle(self, client_socket, address):
        try:
            super().wrap_socket_and_handle(client_socket, address)
        except ssl.SSLEOFError:
            print(f'Unable to handle {address}, will start a client connection to it.')
            lan_mode.start_connection(address[0])
            print('Spawned')


server = Server(
    (settings.SERVER_ADDRESS, settings.SERVER_PORT),
    app.app,
    handler_class=WebSocketHandler,
    **ssl_kwargs
)
print(f'Serving sonoff "cloud" on {settings.SERVER_ADDRESS}:{settings.SERVER_PORT}')
try:
    mqtt.start()
    server.serve_forever()
finally:
    mqtt.stop()
