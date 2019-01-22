from keras.applications import mobilenetv2

from .image_classification import Image_Classification

class MobileNet_V2(Image_Classification):
    def __init__(self, *args, **kwargs):
        Image_Classification.__init__(self, *args, **kwargs)
        if hasattr(self, 'input_shape') == False:
            self.input_shape = (224, 224, 3)
    
    def create_model(self, num_classes):
        model = mobilenetv2.MobileNetV2( weights=None, input_shape=self.input_shape, classes=num_classes )
        return model