from keras.applications import densenet

from .image_classification import Image_Classification

class DenseNet121(Image_Classification):
    def __init__(self, *args, **kwargs):
        Image_Classification.__init__(self, *args, **kwargs)
        if hasattr(self, 'input_shape') == False:
            self.input_shape = (224, 224, 3)
    
    def create_model(self, num_classes):
        model = densenet.DenseNet121( weights=None, input_shape=self.input_shape, classes=num_classes )
        return model

class DenseNet169(Image_Classification):
    def __init__(self, *args, **kwargs):
        Image_Classification.__init__(self, *args, **kwargs)
        if hasattr(self, 'input_shape') == False:
            self.input_shape = (224, 224, 3)
    
    def create_model(self, num_classes):
        model = densenet.DenseNet169( weights=None, input_shape=self.input_shape, classes=num_classes )
        return model

class DenseNet201(Image_Classification):
    def __init__(self, *args, **kwargs):
        Image_Classification.__init__(self, *args, **kwargs)
        if hasattr(self, 'input_shape') == False:
            self.input_shape = (224, 224, 3)
    
    def create_model(self, num_classes):
        model = densenet.DenseNet201( weights=None, input_shape=self.input_shape, classes=num_classes )
        return model