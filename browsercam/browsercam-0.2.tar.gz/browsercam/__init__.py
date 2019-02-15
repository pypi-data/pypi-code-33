import sys
import os
import logging
import threading
import webbrowser
import traceback
from contextlib import contextmanager
from flask import Flask, render_template_string, request, jsonify

sys_stdout = sys.stdout


@contextmanager
def suppress_stdout():
    with open(os.devnull, 'w') as devnull:
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = sys_stdout


@contextmanager
def enable_stdout():
    orig_stdout = sys.stdout
    sys.stdout = sys_stdout
    try:
        yield
    finally:
        sys.stdout = orig_stdout


class Webcam:
    server_host = '0.0.0.0'
    server_port = 5000
    template_file = os.path.join(os.path.dirname(__file__), 'webcam.html')

    def __init__(self):
        self._on_capture = self._on_capture_default

        server = Flask(__name__)
        self.server = server

        @server.route('/', methods=['GET', 'POST'])
        def index():
            # re-enable stdout for debugging
            with enable_stdout():
                if request.method == 'GET':
                    with open(self.template_file) as f:
                        template = f.read()
                        return render_template_string(template)

                elif request.method == 'POST':
                    image = request.files['data'].read()
                    try:
                        return_val = self._on_capture(image)
                    except Exception:
                        traceback.print_exc()

                    if isinstance(return_val, dict):
                        return jsonify(return_val)
                    else:
                        return str(return_val)

        # disable flask logging
        log = logging.getLogger('werkzeug')
        log.disabled = True
        self.server.logger.disabled = True

    def on_capture(self, callback):
        """
        Set the callback function for when an image is captured. When the webcam image is captured,
        the provided function will be called with a `bytes` object containing the image data.
        """
        self._on_capture = callback

    def _on_capture_default(self, image):
        print(
            'Captured image ({} bytes)\n\n'
            'You need to set `on_capture` if you want to do something with the captured image.\n'
            'Please consult the documentation for more details.'.format(len(image))
          )

    def start(self, open_browser=False):
        """
        Start the webcam server and open the browser window.
        """
        def run_server():
            with suppress_stdout():
                self.server.run(host=self.server_host, port=self.server_port)

        thread = threading.Thread(target=run_server)
        thread.start()

        url_host = self.server_host
        if url_host == '0.0.0.0':
            url_host = 'localhost'

        url = 'http://{}:{}/'.format(url_host, self.server_port)
        print('Started webcam at: {}\n'.format(url))

        if open_browser:
            webbrowser.open(url)
