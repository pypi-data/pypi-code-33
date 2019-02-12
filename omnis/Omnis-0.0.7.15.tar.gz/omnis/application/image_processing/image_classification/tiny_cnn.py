from keras.models import Model

from keras.layers import Input, Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D

from .image_classification import Image_Classification


class Tiny_CNN(Image_Classification):
    def __init__(self, *args, **kwargs):
        Image_Classification.__init__(self, *args, **kwargs)
        if hasattr(self, 'input_shape') == False:
            self.input_shape = (32, 32, 3)
    
    def create_model(self, num_classes):
        input_layer = Input(shape=self.input_shape)
        conv1 = Conv2D(32, (3, 3), activation='relu')(input_layer)
        conv2 = Conv2D(64, (3, 3), activation='relu')(conv1)
        pool1 = MaxPooling2D(pool_size=(2, 2))(conv2)
        drop1 = Dropout(0.25)(pool1)
        flat1 = Flatten()(drop1)
        dense1 = Dense(128, activation='relu')(flat1)
        drop2 = Dropout(0.5)(dense1)
        output_layer = Dense(num_classes, activation='softmax')(drop2)

        model = Model(inputs=input_layer, outputs=output_layer)
        return model