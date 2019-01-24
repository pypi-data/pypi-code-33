# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from .Engine import Engine
from keras.preprocessing.image import img_to_array
from keras.applications import imagenet_utils
from PIL import Image
import numpy as np
import requests
import os


class CustomStructured(Engine):

    credentials = {
        "url": "http://173.193.75.3:31520/v1/deployments",
        "username": "xxx",
        "password": "yyy"
    }

    def score(self, binding_details, subscription_details):
        payload = {'fields': ['ID',
                              'Gender',
                              'Status',
                              'Children',
                              'Age',
                              'Customer_Status',
                              'Car_Owner',
                              'Customer_Service',
                              'Business_Area',
                              'Satisfaction'],
                   'values': [[3785,
                               'Male',
                               'S',
                               1,
                               17,
                               'Inactive',
                               'Yes',
                               'The car should have been brought to us instead of us trying to find it in the lot.',
                               'Product: Information',
                               0]]}

        # token = subscription_details['entity']['deployments'][0]['scoring_endpoint']['credentials']['token']
        # headers = subscription_details['entity']['deployments'][0]['scoring_endpoint']['request_headers']
        # headers['Authorization'] = ('Bearer ' + token)

        header = {'Content-Type': 'application/json', 'Authorization': 'Bearer xxx'}
        scoring_url = subscription_details['entity']['deployments'][0]['scoring_endpoint']['url']

        response = requests.post(scoring_url, json=payload, headers=header)

        return payload, response.json(), 25


class CustomUnstructuredImage(Engine):

    credentials = {
        "url": "http://173.193.75.3:31520/v1/deployments",
        "username": "xxx",
        "password": "yyy",
        "header": {"content-type": "application/json"}
    }

    image_path = os.path.join(os.getcwd(), 'datasets', 'images', 'labrador.jpg')

    def score(self, binding_details, subscription_details):
        image = Image.open(self.image_path)

        if image.mode is not "RGB":
            image = image.convert("RGB")

        image = image.resize((224, 224))
        image = img_to_array(image)
        image = np.expand_dims(image, axis=0)
        image = imagenet_utils.preprocess_input(image)
        image_list = image.tolist()

        payload = {'values': image_list}


        # token = subscription_details['entity']['deployments'][0]['scoring_endpoint']['credentials']['token']
        # headers = subscription_details['entity']['deployments'][0]['scoring_endpoint']['request_headers']
        # headers['Authorization'] = ('Bearer ' + token)

        header = {'Content-Type': 'application/json', 'Authorization': 'Bearer xxx'}
        scoring_url = subscription_details['entity']['deployments'][0]['scoring_endpoint']['url']

        response = requests.post(scoring_url, json=payload, headers=header)

        return payload, response.json(), 25


