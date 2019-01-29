# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import os
import json


def check_if_model_exist():
    file_path = os.path.join(os.getcwd(), 'artifacts', 'KerasVGG16', 'vgg16.tar.gz')
    if not os.path.exists(file_path):
        return False
    return True


def get_model_data():

    file_path = os.path.join(os.getcwd(), 'artifacts', 'KerasVGG16', 'vgg16.tar.gz')
    if not os.path.exists(file_path):
        raise FileNotFoundError("vgg16.tar.gz not found. Please use download_model.sh script to download model.")

    return {
        'path': file_path
    }


def get_scoring_payload():
    file_path = os.path.join(os.getcwd(), 'datasets', 'KerasVGG16', 'scoring_payload.json')
    with open(file_path) as f:
        return json.load(f)
