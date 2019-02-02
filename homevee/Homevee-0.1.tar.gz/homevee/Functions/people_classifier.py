#!/usr/bin/python
# -*- coding: utf-8 -*-
import base64
import json
import os
import time
import traceback
from thread import start_new_thread

import cStringIO

from PIL import Image

#from Functions.tensorflow_functions import ar_control_predict
#from Functions.tensorflow_functions.ar_control_retrain import ar_training
from homevee import constants
from Functions.tensorflow_functions import people_predict, people_retrain
from Helper.helper_functions import has_permission
from homevee.constants import DATA_DIR
from homevee.db_utils import get_database_con, set_server_data, get_server_data
from file_utils import create_image

IS_TRAINING_TAG = "PEOPLE_CLASSIFIER_TRAINING_RUNNING"

def upload_images(username, data, img_class, db):
    images = json.loads(data)

    counter = 0

    if(img_class == "-1" or img_class == -1):
        img_class = None

    for image in images:
        filename = "person-" + str(int(time.time())) + "_" + str(counter)

        counter += 1

        image_path = create_image(filename, "people", image, optimize=True)

        with db:
            cur = db.cursor()

            cur.execute("INSERT INTO PEOPLE_LEARNING_DATA (PATH, PERSON_ID) VALUES (:path, :person_id)",
                        {'path': image_path, 'person_id': img_class})

        #print image

    return {'result': 'ok'}

def save_people_class(username, id, data, classname, db):
    return

def classify_person(image_data, db):

    filename = "person-"+str(int(time.time()))

    image_path = create_image(filename, "people", image_data, optimize=True)

    with db:
        cur = db.cursor()

        cur.execute("INSERT INTO PEOPLE_LEARNING_DATA (PATH) VALUES (:path)",
                    {'path': image_path})

    predictions = people_predict.predict(os.path.join(constants.DATA_DIR, image_path))

    for prediction in predictions:
        person_data = get_person_class_data(prediction['prediction'], db)
        print person_data['NAME'] + ": " + str(prediction['confidence'])

    print(image_path)

    person_data = get_person_class_data(predictions[0]['prediction'], db)

    return {'label': person_data['NAME'], 'confidence': str(predictions[0]['confidence']*100)}

def get_person_class_data(id, db):
    with db:
        cur = db.cursor()

        cur.execute("SELECT * FROM PEOPLE_DATA WHERE ID = :id;", {'id': id})

        return cur.fetchone()

def start_people_training(username, db):
    if not has_permission(username, 'admin', db):
        return {'result': 'noadmin'}

    is_training = get_server_data(IS_TRAINING_TAG, db)

    if(is_training is not None and is_training == "true"):
        return {'result': 'alreadytraining'}

    start_new_thread(training_thread, (username, None))

    return {'result': 'ok'}

def training_thread(username, d):
    db = get_database_con()

    set_server_data(IS_TRAINING_TAG, "true", db)

    try:
        people_retrain.people_training(username)
    except:
        traceback.print_exc()

    set_server_data(IS_TRAINING_TAG, "false", db)

def get_people_classes(db):
    with db:
        cur = db.cursor()

        cur.execute("SELECT * FROM PEOPLE_DATA")

        classes = []

        for row in cur.fetchall():
            item = {'id': int(row['ID']), 'name': row['NAME'],}
            classes.append(item)

        item = {'id': None, 'name': 'Nicht zugeordnet'}
        classes.append(item)

        return {'classes': classes}

def get_people_class_images(image_class, show, offset, db):
    param_array = {'limit': show, 'offset': offset}

    with db:
        cur = db.cursor()

        if image_class is None or image_class == "-1" or image_class == -1:
            cur.execute("SELECT * FROM 'PEOPLE_LEARNING_DATA' WHERE PERSON_ID IS NULL OR PERSON_ID = -1 LIMIT :limit OFFSET :offset",
                        param_array)
        else:
            param_array['key'] = image_class
            cur.execute("SELECT * FROM 'PEOPLE_LEARNING_DATA' WHERE PERSON_ID = :key LIMIT :limit OFFSET :offset",
                        param_array)

        images = []

        for img in cur.fetchall():
            images.append(img['ID'])

        return {'images': images}

def delete_people_images(ids, db):
    # todo

    ids = json.loads(ids)

    with db:
        cur = db.cursor()

        for id in ids:
            print "deleting: "+str(id)
            cur.execute("SELECT * FROM PEOPLE_LEARNING_DATA WHERE ID == :id;",
                        {'id': id})
            item = cur.fetchone()
            if (item is not None):
                rel_path = item['PATH']

                image_path = os.path.join(DATA_DIR, rel_path)
                if os.path.exists(image_path):
                    os.remove(image_path)
                else:
                    print image_path+" not found"

                cur.execute("DELETE FROM PEOPLE_LEARNING_DATA WHERE ID == :id;",
                            {'id': id})

    return {'result': 'ok'}

def change_people_image_class(ids, newclass, db):
    if newclass == "-1":
        newclass = None

    ids = json.loads(ids)

    print(ids)

    with db:
        cur = db.cursor()

        for id in ids:
            cur.execute("UPDATE 'PEOPLE_LEARNING_DATA' SET PERSON_ID = :key WHERE ID == :id;",
                        {'key': newclass, 'id': id})

    return {'result': 'ok'}

def get_people_images(image_class, show, offset, db):
    param_array = {'limit': show, 'offset': offset}

    with db:
        cur = db.cursor()

        if image_class == "-1":
            cur.execute("SELECT * FROM 'PEOPLE_LEARNING_DATA' WHERE PERSON_ID IS NULL LIMIT :limit OFFSET :offset",
                        param_array)
        else:
            param_array['key'] = image_class
            cur.execute("SELECT * FROM 'PEOPLE_LEARNING_DATA' WHERE PERSON_ID = :key LIMIT :limit OFFSET :offset",
                        param_array)

        images = []

        for img in cur.fetchall():
            images.append(img['ID'])

        return {'images': images}

def get_people_image(id, db):
    with db:
        cur = db.cursor()

        cur.execute("SELECT PATH FROM 'PEOPLE_LEARNING_DATA' WHERE ID == :id",
                    {'id': id})

        rel_path = cur.fetchone()['PATH']

        path = os.path.join(DATA_DIR, rel_path)
        print("Path: " + path)

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

    prefix = "PEOPLE_"

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

    return {'data': tf_data, 'graph_sizes': people_retrain.get_graph_sizes(),
            'image_sizes' : people_retrain.get_image_sizes()}

def set_performance_settings(username, data, db):
    if not has_permission(username, 'admin', db):
        return {'result': 'noadmin'}

    prefix = "PEOPLE_"

    data = json.loads(data)

    with db:
        cur = db.cursor()

        indices = ['TF_TRAINING_STEPS', 'TF_MODEL_SIZE', 'TF_MODEL_IMAGE_SIZE']

        for index in indices:
            param_array = {'value': data[index], 'key': prefix+index}

            cur.execute("UPDATE OR IGNORE SERVER_DATA SET VALUE = :value WHERE KEY = :key;", param_array)

            cur.execute("INSERT OR IGNORE INTO SERVER_DATA (VALUE, KEY) VALUES (:value, :key);", param_array)

    return {'result':'ok'}