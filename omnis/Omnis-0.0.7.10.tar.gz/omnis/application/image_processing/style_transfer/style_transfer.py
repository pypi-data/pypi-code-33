from keras import backend as K
import keras

from keras.preprocessing.image import load_img, img_to_array
import numpy as np
from scipy.optimize import fmin_l_bfgs_b
import time
import os
import imageio
import cv2
from ...application import Application

class Style_Transfer(Application):
    def __init__(self, input_shape = None, model_path = None):
        if type(model_path) != type(None):
            Application.__init__(self, model_path)
        else:
            Application.__init__(self)
        if type(input_shape) != type(None):
            self.input_shape = input_shape
        else:
            self.input_shape = (224, 224, 3)
        self.loss_value = None
        self.grad_values = None

    def prepare_train_data(self, get_base_image_from = 'directory', get_reference_image_as = 'filepath'):
        assert get_base_image_from in ["directory", "argument"], "get_base_image_from should be either 'directory' or 'argument'."
        assert get_reference_image_as in ["filepath", "ndarray"], "get_reference_image_as should be either 'filepath' or 'ndarray'."

        self.get_base_image_from = get_base_image_from
        self.get_reference_image_as = get_reference_image_as

    def generate(self, base_image_path = None, reference_image_path = None, base_image_array = None, reference_image_array = None,
                output_type = "file", output_path = "result", iterations = 10, total_variation_weight = 1.0, style_weight = 1.0, content_weight = 0.025):
        self.total_variation_weight = total_variation_weight
        self.style_weight = style_weight
        self.content_weight = content_weight

        if self.get_reference_image_as == 'filepath':
            try:
                load_img(reference_image_path)
                reference_image = reference_image_path
            except Exception as e:
                raise e
        else:
            if reference_image_array.ndim == 3:
                reference_image_array = np.array([[reference_image_array]])
            elif reference_image_array.ndim < 4:
                raise ValueError("reference_image_array is not an image ndarray")
            reference_image = reference_image_array

        if self.get_base_image_from == "directory":
            if not os.path.isdir(base_image_path):
                raise FileNotFoundError(base_image_path + " is not an existing directory.")
            parent = os.listdir(base_image_path)
        else:
            if base_image_array.ndim == 3:
                base_image_array = np.array([base_image_array])
            elif base_image_array.ndim < 4:
                raise ValueError("base_image_array is not an image ndarray")
            parent = base_image_array
            
        assert output_type in ["file", "array"], "output_type should be either 'file' or 'array'."
        
        create_result = True
        for child in parent:
            # dimensions of the generated picture.
            if self.get_base_image_from == 'directory':
                width, height = load_img(base_image_path + "/" + child).size
            elif self.get_base_image_from == 'argument':
                width = child[0]
                height = child[1]
            img_nrows = 400
            img_ncols = int(width * img_nrows / height)

            model_type = keras.applications.vgg19

            # get tensor representations of our images
            if self.get_base_image_from == 'directory':
                x = self.preprocess_image(base_image_path + "/" + child, img_nrows, img_ncols, model_type)
            elif self.get_base_image_from == 'argument':
                x = self.preprocess_image(child, img_nrows, img_ncols, model_type)
            base_image = K.variable( x )
            reference_image_tensor = K.variable( self.preprocess_image(reference_image, img_nrows, img_ncols, model_type) )

            # this will contain our generated image
            if K.image_data_format() == 'channels_first':
                self.combination_image = K.placeholder((1, 3, img_nrows, img_ncols))
            else:
                self.combination_image = K.placeholder((1, img_nrows, img_ncols, 3))

            # combine the 3 images into a single Keras tensor
            input_tensor = K.concatenate([base_image, reference_image_tensor, self.combination_image], axis=0)

            # build the VGG16 network with our 3 images as input
            # the model will be loaded with pre-trained ImageNet weights
            model = keras.applications.vgg19.VGG19(input_tensor = input_tensor, weights = 'imagenet', include_top = False)
            print('Model loaded.')

            loss = self.make_loss(model, img_nrows, img_ncols)

            # get the gradients of the generated image wrt the loss
            grads = K.gradients(loss, self.combination_image)

            outputs = [loss]
            if isinstance(grads, (list, tuple)):
                outputs += grads
            else:
                outputs.append(grads)

            self.f_outputs = K.function([self.combination_image], outputs)

            # run scipy-based optimization (L-BFGS) over the pixels of the generated image
            # so as to minimize the neural style loss
            for i in range(iterations):
                print('Start of iteration', i)
                start_time = time.time()
                x, min_val, info = fmin_l_bfgs_b(self.loss, x.flatten(), args = (img_nrows, img_ncols), fprime=self.grads, maxfun=20)
                print('Current loss value:', min_val)
                end_time = time.time()
                print('Iteration %d completed in %ds' % (i, end_time - start_time))
                
            img = self.deprocess_image(x.copy(), img_nrows, img_ncols)
            if output_type == 'array':
                if create_result:
                    img = cv2.resize(img, (224, 224))
                    result = np.array([img])
                    create_result = False
                else:
                    img = cv2.resize(img, (224, 224))
                    img = np.array([img])
                    result = np.concatenate((result, img))
            elif output_type == 'file':
                # save current generated image
                fname = os.getcwd() + "/" + output_path + "/" + child
                if not os.path.exists(os.path.dirname(fname)):
                    os.makedirs(os.path.dirname(fname))
                imageio.imwrite(fname, img)
                print('Image saved as', fname)

        if output_type == 'array':
            return result
        else:
            return

    def preprocess_image(self, image_path, img_nrows, img_ncols, model_type):
        if type(image_path) != np.ndarray:
            img = load_img(image_path, target_size=(img_nrows, img_ncols))
            img = img_to_array(img)
        img = np.expand_dims(img, axis=0)
        img = model_type.preprocess_input(img)
        return img

    def deprocess_image(self, x, img_nrows, img_ncols):
        if K.image_data_format() == 'channels_first':
            x = x.reshape((3, img_nrows, img_ncols))
            x = x.transpose((1, 2, 0))
        else:
            x = x.reshape((img_nrows, img_ncols, 3))
        # Remove zero-center by mean pixel
        x[:, :, 0] += 103.939
        x[:, :, 1] += 116.779
        x[:, :, 2] += 123.68
        # 'BGR'->'RGB'
        x = x[:, :, ::-1]
        x = np.clip(x, 0, 255).astype('uint8')
        return x

    # the gram matrix of an image tensor (feature-wise outer product)
    def gram_matrix(self, x):
        assert K.ndim(x) == 3
        if K.image_data_format() == 'channels_first':
            features = K.batch_flatten(x)
        else:
            features = K.batch_flatten(K.permute_dimensions(x, (2, 0, 1)))
        gram = K.dot(features, K.transpose(features))
        return gram

    # an auxiliary loss function
    # designed to maintain the "content" of the
    # base image in the generated image
    def content_loss(self, base, combination):
        return K.sum(K.square(combination - base))

    # the "style loss" is designed to maintain
    # the style of the reference image in the generated image.
    # It is based on the gram matrices (which capture style) of
    # feature maps from the style reference image
    # and from the generated image
    def style_loss(self, style, combination, img_nrows, img_ncols):
        assert K.ndim(style) == 3
        assert K.ndim(combination) == 3
        S = self.gram_matrix(style)
        C = self.gram_matrix(combination)
        channels = 3
        size = img_nrows * img_ncols
        return K.sum(K.square(S - C)) / (4. * (channels ** 2) * (size ** 2))

    # the 3rd loss function, total variation loss,
    # designed to keep the generated image locally coherent
    def total_variation_loss(self, x, img_nrows, img_ncols):
        assert K.ndim(x) == 4
        if K.image_data_format() == 'channels_first':
            a = K.square(x[:, :, :img_nrows - 1, :img_ncols - 1] - x[:, :, 1:, :img_ncols - 1])
            b = K.square(x[:, :, :img_nrows - 1, :img_ncols - 1] - x[:, :, :img_nrows - 1, 1:])
        else:
            a = K.square(x[:, :img_nrows - 1, :img_ncols - 1, :] - x[:, 1:, :img_ncols - 1, :])
            b = K.square(x[:, :img_nrows - 1, :img_ncols - 1, :] - x[:, :img_nrows - 1, 1:, :])
        return K.sum(K.pow(a + b, 1.25))

    def make_loss(self, model, img_nrows, img_ncols):
        # get the symbolic outputs of each "key" layer (we gave them unique names).
        outputs_dict = dict([(layer.name, layer.output) for layer in model.layers])

        # combine these loss functions into a single scalar
        loss = K.variable(0.)
        layer_features = outputs_dict['block5_conv2']
        base_image_features = layer_features[0, :, :, :]
        combination_features = layer_features[2, :, :, :]
        loss += self.content_weight * self.content_loss(base_image_features, combination_features)

        feature_layers = ['block1_conv1', 'block2_conv1', 'block3_conv1', 'block4_conv1', 'block5_conv1']
        for layer_name in feature_layers:
            layer_features = outputs_dict[layer_name]
            style_reference_features = layer_features[1, :, :, :]
            combination_features = layer_features[2, :, :, :]
            sl = self.style_loss(style_reference_features, combination_features, img_nrows, img_ncols)
            loss += (self.style_weight / len(feature_layers)) * sl
        loss += self.total_variation_weight * self.total_variation_loss(self.combination_image, img_nrows, img_ncols)
        return loss

    def loss(self, x, img_nrows, img_ncols):
        assert self.loss_value is None
        loss_value, grad_values = self.eval_loss_and_grads(x, img_nrows, img_ncols)
        self.loss_value = loss_value
        self.grad_values = grad_values
        return self.loss_value

    def grads(self, x, img_nrows, img_ncols):
        assert self.loss_value is not None
        grad_values = np.copy(self.grad_values)
        self.loss_value = None
        self.grad_values = None
        return grad_values

    def eval_loss_and_grads(self, x, img_nrows, img_ncols):
        if K.image_data_format() == 'channels_first':
            x = x.reshape((1, 3, img_nrows, img_ncols))
        else:
            x = x.reshape((1, img_nrows, img_ncols, 3))
        outs = self.f_outputs([x])
        loss_value = outs[0]
        if len(outs[1:]) == 1:
            grad_values = outs[1].flatten().astype('float64')
        else:
            grad_values = np.array(outs[1:]).flatten().astype('float64')
        return loss_value, grad_values
