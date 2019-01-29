from keras.applications import xception

from .image_classification import Image_Classification

class Xception(Image_Classification):
    def __init__(self, *args, **kwargs):
        Image_Classification.__init__(self, *args, **kwargs)
        if hasattr(self, 'input_shape') == False:
            self.input_shape = (299, 299, 3)
    
    def create_model(self, num_classes):
        model = xception.Xception( weights=None, input_shape=self.input_shape, classes=num_classes )
        return model