# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from .AbstractModel import AbstractModel
import os
import random
from keras.datasets import mnist
import numpy as np

class Mnist(AbstractModel):

    model_path = os.path.join(os.getcwd(), 'artifacts', 'core_ml', 'keras', 'mnistCNN.h5.tgz')
    (x_train, y_train), (x_test, y_test) = mnist.load_data()

    def publish_to_wml(self, wml_client):
        return wml_client.repository.store_model(model=self.model_path, meta_props=self.get_model_props(wml_client))

    def get_model_props(self, wml_client):
        return {
            wml_client.repository.ModelMetaNames.NAME: "Keras mnist model",
            wml_client.repository.ModelMetaNames.FRAMEWORK_NAME: "tensorflow",
            wml_client.repository.ModelMetaNames.FRAMEWORK_VERSION: "1.5",
            wml_client.repository.ModelMetaNames.RUNTIME_NAME: "python",
            wml_client.repository.ModelMetaNames.RUNTIME_VERSION: "3.5",
            wml_client.repository.ModelMetaNames.FRAMEWORK_LIBRARIES: [{'name': 'keras', 'version': '2.1.3'}],
        }

    def get_scoring_payload(self):

        index_1 = random.randint(0, len(self.x_test) - 1)
        index_2 = random.randint(0, len(self.x_test) - 1)

        image_1 = np.expand_dims(self.x_test[index_1], axis=2)
        image_2 = np.expand_dims(self.x_test[index_2], axis=2)

        print('Image: ' + str(image_1.tolist()))
        print('Image: ' + str(image_2.tolist()))

        return {'values': [image_1.tolist(), image_2.tolist()]}