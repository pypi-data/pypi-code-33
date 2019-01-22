from keras.applications import inception_resnet_v2

from .image_classification import Image_Classification

class Inception_ResNet_V2(Image_Classification):
    def __init__(self, *args, **kwargs):
        Image_Classification.__init__(self, *args, **kwargs)
        if hasattr(self, 'input_shape') == False:
            self.input_shape = (299, 299, 3)
    
    def create_model(self, num_classes):
        model = inception_resnet_v2.InceptionResNetV2( weights=None, input_shape=self.input_shape, classes=num_classes )
        return model