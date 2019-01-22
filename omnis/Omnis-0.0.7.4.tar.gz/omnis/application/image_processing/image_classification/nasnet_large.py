from keras.applications import nasnet

from .image_classification import Image_Classification

class NASNet_Large(Image_Classification):
    def __init__(self, *args, **kwargs):
        Image_Classification.__init__(self, *args, **kwargs)
        if hasattr(self, 'input_shape') == False:
            self.input_shape = (331, 331, 3)
    
    def create_model(self, num_classes):
        model = nasnet.NASNetLarge( weights=None, input_shape=self.input_shape, classes=num_classes )
        return model