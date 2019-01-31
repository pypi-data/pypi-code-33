import os, shutil, re
from flask import Flask, request, jsonify
from .settings import (
    BASE_DIR,
    SAFE_DELETION,
)


app = Flask(__name__)
name_regexp = re.compile('^[a-zA-Z0-9][a-zA-Z0-9\_\.\-]{0,40}$')


def full_path(name):
    return os.path.join(BASE_DIR, name)


@app.route('/Plugin.Activate', methods=['POST'])
def plugin_activate():
    return jsonify(
        {
            'Implements': ['VolumeDriver']
        }
    )


@app.route('/VolumeDriver.Create', methods=['POST'])
def create():
    data = request.get_json(force=True)
    path = full_path(data['Name'])

    if os.path.isdir(path):
        err = 'Volume is already created'
    else:
        try:
            os.mkdir(path)
        except Exception as e:
            err = str(e)
        else:
            err = ''

    return jsonify(
        {
            'Err': err
        }
    )



@app.route('/VolumeDriver.Remove', methods=['POST'])
def remove():
    data = request.get_json(force=True)
    name = data['Name']
    path = full_path(name)

    try:
        if SAFE_DELETION:
            new_name = '_' + name
            new_path = full_path(new_name)
            shutil.move(path, new_path)
        else:
            shutil.rmtree(name)
    except Exception as e:
        err = str(e)
    else:
        err = ''

    return jsonify(
        {
            'Err': err
        }
    )


@app.route('/VolumeDriver.Path', methods=['POST'])
@app.route('/VolumeDriver.Mount', methods=['POST'])
def mount():
    data = request.get_json(force=True)
    path = full_path(data['Name'])

    if os.path.isdir(path):
        err = ''
    else:
        err = 'Volume doesn\'t exist'

    return jsonify(
        {
            'Mountpoint': path,
            'Err': err
        }
    )


@app.route('/VolumeDriver.Unmount', methods=['POST'])
def unmount():
    data = request.get_json(force=True)
    path = full_path(data['Name'])

    if os.path.isdir(path):
        err = ''
    else:
        err = 'Volume doesn\'t exist'

    return jsonify(
        {
            'Err': err
        }
    )


@app.route('/VolumeDriver.Get', methods=['POST'])
def get():
    data = request.get_json(force=True)
    name = data['Name']
    path = full_path(name)

    if os.path.isdir(path):
        err = ''
    else:
        err = 'Volume doesn\'t exist'

    return jsonify(
        {
            'Volume': {
                'Name': name,
                'MountPoint': path,
                'Status': {}
            },
            'Err': err
        }
    )


@app.route('/VolumeDriver.List', methods=['POST'])
def list():
    try:
        names = [
            name for name in os.listdir(BASE_DIR)
            if name_regexp.match(name)
        ]

        volumes = []
        for name in names:
            path = full_path(name)

            if os.path.isdir(path):
                volumes.append(
                    {
                        'Name': name,
                        'MountPoint': path
                    }
                )
    except Exception as e:
        return jsonify(
            {
                'Err': str(e)
            }
        )

    return jsonify(
        {
            'Volumes': volumes,
            'Err': ''
        }
    )


@app.route('/VolumeDriver.Capabilities', methods=['POST'])
def capabilities():
    return jsonify(
        {
            'Capabilities': {
                'Scope': 'global'
            }
        }
    )

if __name__ == "__main__":
    app.run(host='0.0.0.0')
