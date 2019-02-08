from keras.applications import inception_v3

from .image_classification import Image_Classification

class Inception_V3(Image_Classification):
    def __init__(self, *args, **kwargs):
        Image_Classification.__init__(self, *args, **kwargs)
        if hasattr(self, 'input_shape') == False:
            self.input_shape = (299, 299, 3)
    
    def create_model(self, num_classes):
        model = inception_v3.InceptionV3( weights=None, input_shape=self.input_shape, classes=num_classes )
        return model