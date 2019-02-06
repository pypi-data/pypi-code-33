import os, shutil, re, time
from flask import Flask, request, jsonify
from .settings import (
    BASE_DIR,
    SAFE_DELETION,
    GLOBAL_SCOPE,
    TRACK_MOUNTS,
)


app = Flask(__name__)


name_regexp = re.compile('^[a-zA-Z0-9][a-zA-Z0-9\_\.\-]{0,200}$')


def mk_full_path(name):
    return os.path.join(BASE_DIR, name)


def mk_metadata_path(name):
    metadata_dirname = '__{}'.format(name)
    return mk_full_path(metadata_dirname)


def check_name(name):
    if name_regexp.match(name):
        return ''
    else:
        return 'Name {} is wrong'.format(name)


def drv_resp(error, extra_data=None):
    if extra_data is None:
        extra_data = {}

    return jsonify(
        {
            'Err': error,
            **extra_data
        }
    )


@app.route('/Plugin.Activate', methods=['POST'])
def plugin_activate():
    return jsonify(
        {
            'Implements': ['VolumeDriver']
        }
    )


@app.route('/VolumeDriver.Capabilities', methods=['POST'])
def capabilities():
    return jsonify(
        {
            'Capabilities': {
                'Scope': 'global' if GLOBAL_SCOPE else 'local'
            }
        }
    )


@app.route('/VolumeDriver.Create', methods=['POST'])
def create():
    data = request.get_json(force=True)
    name = data['Name']
    path = mk_full_path(name)

    err = check_name(name)
    if err:
        return drv_resp(err)

    try:
        os.mkdir(path)
    except FileExistsError as e:
        if os.path.isdir(path):
            err = ''
        else:
            err = str(e) or e.__class__.__name__
    except Exception as e:
        err = str(e) or e.__class__.__name__
    else:
        err = ''

    return drv_resp(err)


@app.route('/VolumeDriver.Remove', methods=['POST'])
def remove():
    data = request.get_json(force=True)
    name = data['Name']
    path = mk_full_path(name)
    metadata_dir_path = mk_metadata_path(name)

    err = check_name(name)
    if err:
        return drv_resp(err)

    try:
        mounters = os.listdir(metadata_dir_path)

        if mounters:
            mounters_info = str(mounters[:5])
            err = 'volume is in use - {}'.format(mounters_info)
            return drv_resp(err)
    except FileNotFoundError:
        pass
    except Exception as e:
        err = str(e) or e.__class__.__name__
        return drv_resp(err)

    try:
        if SAFE_DELETION:
            ts = int(time.time() * 1000)
            new_name = '_{}_{}'.format(name, ts)
            new_path = mk_full_path(new_name)
            os.rename(path, new_path)
        else:
            shutil.rmtree(path)

        try:
            shutil.rmtree(metadata_dir_path)
        except FileNotFoundError:
            pass
    except Exception as e:
        err = str(e) or e.__class__.__name__
    else:
        err = ''

    return drv_resp(err)


@app.route('/VolumeDriver.Mount', methods=['POST'])
def mount():
    data = request.get_json(force=True)
    name = data['Name']
    path = mk_full_path(name)

    err = check_name(name)
    if err:
        return drv_resp(err)

    if os.path.isdir(path):
        if TRACK_MOUNTS:
            try:
                metadata_dir_path = mk_metadata_path(name)
                try:
                    os.mkdir(metadata_dir_path)
                except FileExistsError:
                    pass

                mounter_id = data['ID']
                mount_indication_path = os.path.join(metadata_dir_path, mounter_id)
                os.mknod(mount_indication_path)
            except Exception as e:
                err = str(e) or e.__class__.__name__
            else:
                err = ''
        else:
            err = ''
    else:
        err = 'No such volume: {}'.format(name)

    return drv_resp(err, extra_data={'Mountpoint': path})


@app.route('/VolumeDriver.Path', methods=['POST'])
def path():
    data = request.get_json(force=True)
    name = data['Name']

    err = check_name(name)
    if err:
        return drv_resp(err)

    if os.path.isdir(path):
        err = ''
    else:
        err = 'No such volume: {}'.format(name)

    return drv_resp(err, extra_data={'Mountpoint': path})


@app.route('/VolumeDriver.Unmount', methods=['POST'])
def unmount():
    data = request.get_json(force=True)
    name = data['Name']
    path = mk_full_path(name)

    err = check_name(name)
    if err:
        return drv_resp(err)

    if os.path.isdir(path):
        if TRACK_MOUNTS:
            try:
                metadata_dir_path = mk_metadata_path(name)
                mounter_id = data['ID']
                mount_indication_path = os.path.join(metadata_dir_path, mounter_id)
                os.remove(mount_indication_path)
            except FileNotFoundError:
                err = ''
            except Exception as e:
                err = str(e) or e.__class__.__name__
            else:
                err = ''
    else:
        err = 'No such volume: {}'.format(name)

    return drv_resp(err)


@app.route('/VolumeDriver.Get', methods=['POST'])
def get():
    data = request.get_json(force=True)
    name = data['Name']
    path = mk_full_path(name)

    err = check_name(name)
    if err:
        return drv_resp(err)

    if os.path.isdir(path):
        return drv_resp(
            '',
            extra_data={
                'Volume': {
                    'Name': name,
                    'MountPoint': path,
                    'Status': {
                        'meow': 'mix',
                        'kitty': 'cat'
                    }
                }
            }
        )
    else:
        err = 'No such volume: {}'.format(name)
        return drv_resp(err)


@app.route('/VolumeDriver.List', methods=['POST'])
def list():
    try:
        names = [
            name for name in os.listdir(BASE_DIR)
            if name_regexp.match(name)
        ]

        volumes = []
        for name in names:
            path = mk_full_path(name)

            if os.path.isdir(path):
                volumes.append(
                    {
                        'Name': name,
                        'MountPoint': path
                    }
                )
    except Exception as e:
        err = str(e) or e.__class__.__name__
        return drv_resp(err)

    return drv_resp('', extra_data={'Volumes': volumes})


if __name__ == "__main__":
    app.run(host='0.0.0.0')
