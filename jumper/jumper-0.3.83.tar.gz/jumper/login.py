import tornado.ioloop
import tornado.web
import json
import webbrowser
import socket
import signal
import sys

from .config import set_token, DEFAULT_CONFIG

URL = "https://vlab.jumper.io"
# URL = "http://localhost:3000"
CLI_LOGIN_URL = URL + '/cli_login'
GET_STARTED_URL = URL + '/getstarted'
token = None

close_tornado = False


class TokenHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "*")
        self.set_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')

    def get(self):
        global token
        token = self.request.query_arguments['code'][0]
        self.write('Login Success, please close the tab/windows.')
        self.set_status(200)
        tornado.ioloop.IOLoop.current().stop()

    def post(self):
        global token
        data = json.loads(self.request.body)
        token = data['token']
        self.write('OK')
        tornado.ioloop.IOLoop.current().stop()

    def options(self):
        self.set_status(204)
        self.finish()


def try_exit():
    if close_tornado:
        tornado.ioloop.IOLoop.current().stop()


def sig_handler(sig, frame):
    global close_tornado
    close_tornado = True


def token_server():
    global close_tornado
    global token

    token = None
    app = tornado.web.Application([(r"/token", TokenHandler)])
    port = choose_port()
    server = app.listen(port)
    webbrowser.get()
    webbrowser.open_new('{}/{}'.format(CLI_LOGIN_URL, port))

    tornado.ioloop.PeriodicCallback(try_exit, 100).start()

    close_tornado = False
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)
    tornado.ioloop.IOLoop.current().start()

    server.stop()

    if token is None:
        raise ValueError('Could not get token on login')
    return token


def choose_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    addr, port = s.getsockname()
    s.close()
    return port


def login(no_browser=False):
    global token
    try:
        if no_browser:
            raise webbrowser.Error
        token = token_server()
    except webbrowser.Error:
        print("Could not open browser for automatic login, fallback to manual login.")
        print("Please login to your account at https://app.jumper.io, and copy your token from the user info menu at the top-right corner")

        from builtins import input
        new_token = input("Enter token: ")
        if new_token == '':
            raise ValueError("No token was received")
        token = new_token

    set_token(token)
    print("Token has been saved to {}".format(DEFAULT_CONFIG))
    print("Login successful")
    return token


if __name__ == "__main__":
    print(token_server())
