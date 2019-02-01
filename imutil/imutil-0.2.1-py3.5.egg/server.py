import flask

app = flask.Flask(__name__)

@app.route('/')
def main_page():
    return flask.render_template('index.html')

@app.route('/img')
def get_img():
    file_content = open('/tmp/imutil.jpg', 'rb')
    return flask.Response(file_content, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True, port=8000)
