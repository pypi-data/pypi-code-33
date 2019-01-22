import keras
from keras import backend as K
from PIL import Image
import requests
from io import BytesIO
import matplotlib as mpl
mpl.use('TkAgg')
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import cv2
import numpy as np

class NeuralTransformer:

    """
    Class which performs transfer learning on photographs from url links
    using xception neural network
    """

    def __init__(self,path_to_images, type_of_nn="xception"):
        """
        :param path_to_images:
        List of urls to photographs
        """
        self.path_to_images = path_to_images
        self.type_of_nn = type_of_nn
    def fit_neural(self):
        """
        Loads images for training
        Remember about resizing and normalizing
        Factor of 255 due to 8-bit colors coding
        Define function to fit xception neural net
        :return:
        features extracted from last layer
        """
        if self.type_of_nn=='xception':
            model = keras.applications.xception.Xception(include_top=False, weights='imagenet',
                                                        input_shape=(299, 299, 3))
        elif self.type_of_nn=='mobile':
            model = keras.applications.xception.Xception(include_top=False, weights='imagenet',
                                                         input_shape=(224, 224, 3))
        if len(self.path_to_images) == 1:
            image_path = self.path_to_images[0]
            response = requests.get(image_path)
            img = Image.open(BytesIO(response.content))
            if self.type_of_nn=='xception':
                x = cv2.resize(np.asanyarray(img),(299, 299)).reshape(-1, 299, 299, 3)/255.0
                pred = model.predict(x).reshape(-1,)
            elif self.type_of_nn=='mobile':
                x = cv2.resize(np.asanyarray(img), (224, 224)).reshape(-1, 224, 224, 3) / 255.0
                pred = model.predict(x).reshape(-1, )
            K.clear_session()
            return np.array(pred)

        else:
            images_as_arrays = []
            for image_path in self.path_to_images:
                response = requests.get(image_path)
                img = Image.open(BytesIO(response.content))
                x = cv2.resize(np.asanyarray(img),(299,299)).reshape(-1,299,299,3)/ 255.0
                images_as_arrays.append(x)

            images_ccn_features = []
            for img in images_as_arrays:
                images_ccn_features.append(model.predict(img).reshape(-1,))
            images_ccn_features = np.array(images_ccn_features)
            #Clear session in order to work in app
            K.clear_session()
            return (images_ccn_features)

    def show_photographs(self,embedding):
        """
        :param embedding:
         embedding created by dimensionality reduction algorithm
        :return:
        Two dimensional plot which shows photographs assigned to embeddings
        """
        images = self.path_to_images[:100]
        f, ax = plt.subplots(figsize=(12, 12))
        for index in range(len(images)):
            img = plt.imread(images[index])
            img = OffsetImage(img, zoom=0.05)
            ab = AnnotationBbox(img, (embedding[index, 0], embedding[index, 1]),xycoords='data', frameon=False)
            ax.add_artist(ab)
            ax.update_datalim(np.column_stack([embedding[:, 0], embedding[:, 1]]))
            ax.autoscale()

