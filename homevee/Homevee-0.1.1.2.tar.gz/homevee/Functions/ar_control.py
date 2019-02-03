#!/usr/bin/python
# -*- coding: utf-8 -*-
import base64
import json
import time
import traceback
from thread import start_new_thread
import cStringIO
import os
from PIL import Image
from homevee import constants
from homevee.DeviceAPI.heating import get_thermostats
from homevee.DeviceAPI.get_modes import get_modes
from homevee.DeviceAPI.rgb_control import get_rgb_device
from homevee.Functions.tensorflow_functions import ar_control_predict, ar_control_retrain
from homevee.DeviceAPI.set_modes import set_modes
from homevee.Helper.helper_functions import has_permission
from homevee.Functions.condition_actions.actions import run_scene
from homevee.constants import DATA_DIR
from homevee.db_utils import get_server_data, get_database_con, set_server_data
from homevee.device_types import *
from homevee.file_utils import create_image

IS_TRAINING_TAG = "AR_CONTROL_TRAINING_RUNNING"

def upload_images(username, data, img_class, db):
    images = json.loads(data)

    counter = 0

    if (img_class == "-1" or img_class == -1):
        img_class = None

    for image in images:
        filename = "device-" + str(int(time.time())) + "_" + str(counter)

        counter += 1

        image_path = create_image(filename, "ar_control", image, optimize=True)

        with db:
            cur = db.cursor()

            cur.execute("INSERT INTO AR_CONTROL_LEARNING_DATA (PATH, CONTROL_KEY) VALUES (:path, :class)",
                        {'path': image_path, 'class': img_class})
        #print image

    return {'result': 'ok'}

def save_ar_control_class(username, id, data, classname, db):
    if not has_permission(username, 'admin', db):
        return {'result': 'noadmin'}

    with db:
        cur = db.cursor()

        params = {'name': classname, 'data': data}

        if id is not None and id is not "" and id != "-1":
            params['id'] = id
            cur.execute("UPDATE AR_CONTROL_CLASSES SET NAME = :name, CONTROL_DATA = :data WHERE ID = :id",
                        params)
        else:
            cur.execute("INSERT INTO AR_CONTROL_CLASSES (NAME, CONTROL_DATA) VALUES (:name, :data)",
                        params)

    return {'result': 'ok'}

def ar_control(username, image_data, db):
    filename = "device-"+str(int(time.time()))

    image_path = create_image(filename, "ar_control", image_data, optimize=True)

    with db:
        cur = db.cursor()

        cur.execute("INSERT INTO AR_CONTROL_LEARNING_DATA (PATH) VALUES (:path)",
                    {'path': image_path})

    predictions = ar_control_predict.predict(os.path.join(constants.DATA_DIR, image_path))

    class_data = get_ar_class_data(predictions[0]['prediction'], db)

    print(image_path)
    print class_data['NAME'] + ": " + str(predictions[0]['confidence']*100)

    print class_data

    data = run_ar_command(username, class_data['CONTROL_DATA'], db)

    return data

def run_ar_command(username, data, db):
    data = json.loads(data)

    if data['type'] == "scene":
        run_scene(username, data['id'], db)
    elif data['type'] in [FUNKSTECKDOSE, URL_TOGGLE, URL_SWITCH, ZWAVE_SWITCH]:
        mode = get_modes(username, None, data['type'], data['id'], db)

        if mode is 0:
            mode = 1
        else:
            mode = 0

        set_modes(username, data['type'], data['id'], str(mode), db)

        return {'action': None}
    elif data['type'] in [MAX_THERMOSTAT, ZWAVE_THERMOSTAT]:
        thermostat_data = get_thermostats(username, None, data['type'], data['id'], db)
        return {'action': 'heating', 'data': thermostat_data, 'type': data['type'], 'id': data['id']}
    elif data['type'] in [PHILIPS_HUE_LIGHT, URL_RGB_LIGHT]:
        rgb_data = get_rgb_device(username, data['type'], data['id'], db)
        return {'action': 'rgb', 'data': rgb_data, 'type': data['type'], 'id': data['id']}
    else:
        return {'error': 'nosuchaction'}

def get_ar_class_data(id, db):
    with db:
        cur = db.cursor()

        cur.execute("SELECT * FROM AR_CONTROL_CLASSES WHERE ID = :id;", {'id': id})

        return cur.fetchone()

def start_ar_training(username, db):
    if not has_permission(username, 'admin', db):
        return {'result': 'noadmin'}

    is_training = get_server_data(IS_TRAINING_TAG, db)

    if (is_training is not None and is_training == "true"):
        return {'result': 'alreadytraining'}

    start_new_thread(training_thread, (username, None))

    return {'result': 'ok'}


def training_thread(username, d):
    db = get_database_con()

    set_server_data(IS_TRAINING_TAG, "true", db)

    try:
        ar_control_retrain.ar_training(username)
    except:
        traceback.print_exc()

    set_server_data(IS_TRAINING_TAG, "false", db)

def get_ar_control_classes(db):
    with db:
        cur = db.cursor()

        cur.execute("SELECT * FROM 'AR_CONTROL_CLASSES'")

        classes = []

        for row in cur.fetchall():
            item = {'id': int(row['ID']), 'name': row['NAME'], 'data': row['CONTROL_DATA']}
            classes.append(item)

        item = {'id': None, 'name': 'Nicht zugeordnet'}
        classes.append(item)

        return {'classes': classes}

def get_ar_control_class_images(image_class, show, offset, db):
    param_array = {'limit': show, 'offset': offset}

    with db:
        cur = db.cursor()

        if image_class is None or image_class == "-1" or image_class == -1:
            cur.execute("SELECT * FROM 'AR_CONTROL_LEARNING_DATA' WHERE CONTROL_KEY IS NULL OR CONTROL_KEY = -1 LIMIT :limit OFFSET :offset",
                        param_array)
        else:
            param_array['key'] = image_class
            cur.execute("SELECT * FROM 'AR_CONTROL_LEARNING_DATA' WHERE CONTROL_KEY = :key LIMIT :limit OFFSET :offset",
                        param_array)

        images = []

        for img in cur.fetchall():
            images.append(img['ID'])

        return {'images': images}

def change_ar_image_class(ids, newclass, db):
    if newclass == "-1":
        newclass = None

    ids = json.loads(ids)

    print(ids)

    with db:
        cur = db.cursor()

        for id in ids:
            cur.execute("UPDATE 'AR_CONTROL_LEARNING_DATA' SET CONTROL_KEY = :key WHERE ID == :id;",
                        {'key': newclass, 'id': id})

    return {'result': 'ok'}

def delete_ar_control_images(ids, db):
    #todo

    ids = json.loads(ids)

    with db:
        cur = db.cursor()

        for id in ids:
            print "deleting: "+str(id)
            cur.execute("SELECT * FROM AR_CONTROL_LEARNING_DATA WHERE ID == :id;",
                        {'id': id})
            item = cur.fetchone()
            if(item is not None):
                rel_path = item['PATH']

                image_path = os.path.join(DATA_DIR, rel_path)
                if os.path.exists(image_path):
                    os.remove(image_path)
                else:
                    print image_path+" not found"

                cur.execute("DELETE FROM AR_CONTROL_LEARNING_DATA WHERE ID == :id;",
                            {'id': id})

    return {'result': 'ok'}

def get_ar_control_image(id, db):
    with db:
        cur = db.cursor()

        cur.execute("SELECT PATH FROM 'AR_CONTROL_LEARNING_DATA' WHERE ID == :id",
                    {'id': id})

        rel_path = cur.fetchone()['PATH']

        path = os.path.join(DATA_DIR, rel_path)
        print("Path: "+path)

        im = Image.open(path)

        size = 50

        image_dimensions = size, size

        im.thumbnail(image_dimensions, Image.ANTIALIAS)

        buffer = cStringIO.StringIO()
        im.save(buffer, format="JPEG")
        encoded_string = base64.b64encode(buffer.getvalue())

        im.close()

        #with open(path, "rb") as image_file:
        #    encoded_string = base64.b64encode(image_file.read())

    return {'imagedata': encoded_string}

def get_performance_settings(username, db):
    if not has_permission(username, 'admin', db):
        return {'status': 'noadmin'}

    prefix = "AR_"

    tf_data = {}

    with db:
        cur = db.cursor()

        indices = ['TF_TRAINING_STEPS', 'TF_MODEL_SIZE', 'TF_MODEL_IMAGE_SIZE']

        for index in indices:
            cur.execute("SELECT VALUE FROM SERVER_DATA WHERE KEY = :key",
                        {'key': prefix+index})

            result = cur.fetchone()
            if(result is not None and 'VALUE' in result):
                tf_data[index] = result['VALUE']

    return {'data': tf_data, 'graph_sizes': ar_control_retrain.get_graph_sizes(),
            'image_sizes' : ar_control_retrain.get_image_sizes()}

def set_performance_settings(username, data, db):
    if not has_permission(username, 'admin', db):
        return {'result': 'noadmin'}

    prefix = "AR_"

    data = json.loads(data)

    with db:
        cur = db.cursor()

        indices = ['TF_TRAINING_STEPS', 'TF_MODEL_SIZE', 'TF_MODEL_IMAGE_SIZE']

        for index in indices:
            param_array = {'value': data[index], 'key': prefix+index}

            cur.execute("UPDATE OR IGNORE SERVER_DATA SET VALUE = :value WHERE KEY = :key;", param_array)

            cur.execute("INSERT OR IGNORE INTO SERVER_DATA (VALUE, KEY) VALUES (:value, :key);", param_array)

    return {'result':'ok'}