import json
import os

from flask import Flask, send_file

app = Flask(__name__, static_folder='', static_url_path='')


@app.route("/get_data", methods=['POST', 'GET'])
def get_data():
    data = scatter3d.get_data()
    return data


@app.route('/', methods=['POST', 'GET'])
def upload():
    return send_file('./index.html')


class Scatter3d(object):

    def __init__(self, host="127.0.0.1", port=80):
        self.host = host
        self.port = port

    def run(self):
        app.run(host=self.host, port=self.port)

    def set_data(self, x, y, z):
        self.x = x.tolist()
        self.y = y.tolist()
        self.z = z.tolist()

    def get_data(self):
        data = {"x": self.x, "y": self.y, "z": self.z}
        return json.dumps(data, ensure_ascii=False)


scatter3d = Scatter3d()
