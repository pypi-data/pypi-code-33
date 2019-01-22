import json

from flask import Flask, render_template

app = Flask(__name__, template_folder="", static_folder="", static_url_path="")


@app.route("/get_data", methods=['POST', 'GET'])
def get_data():
    data = scatter3d.get_data()
    return data


@app.route('/', methods=['POST', 'GET'])
def init():
    speed = 0.0005
    if not scatter3d.autorotation is None:
        speed = scatter3d.autorotation
    else:
        speed = 0
    colors = {"start": scatter3d.start_color, "end": scatter3d.end_color}
    return render_template('index.html', colors=colors, speed=speed)


class Scatter3d(object):
    start_color = "#00ff05"
    end_color = "#fff500"
    autorotation = None

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
