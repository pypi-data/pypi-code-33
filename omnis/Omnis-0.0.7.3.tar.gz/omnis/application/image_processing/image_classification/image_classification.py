import keras

from keras.preprocessing.image import ImageDataGenerator
import numpy

import cv2

from ....lib.general_lib import reverse_dict
from ....lib.image_lib import directory_images_to_arrays

from ...application import Application


class Image_Classification(Application):
    """This class is a super class of cnn models.
    """

    def __init__(self, input_shape = None, model_path = None):
        """initializes a CNN model for image classification.
        
        Arguments:
            Application {class} -- A super class of Image_Classification.
        
        Keyword Arguments:
            input_shape {tuple or None} --
                An input shape of image classification model.
                If you do not set an input shape, default input shape of each model will be applied.
                (default: {None})
            model_path {str} -- A path of application file. (default: {None})
        """
        if type(model_path) != type(None):
            Application.__init__(self, model_path)
            return
        if type(input_shape) != type(None):            
            self.input_shape = input_shape
        Application.__init__(self)

    def create_class_indices(self, unique_classes):
        class_indices = dict()
        for i in range(unique_classes.shape[0]):
            class_indices[unique_classes[i]] = i
        return class_indices

    def create_image_data_generator(self, featurewise_center=False,  # set input mean to 0 over the dataset
            samplewise_center=False,  # set each sample mean to 0
            featurewise_std_normalization=False,  # divide inputs by std of the dataset
            samplewise_std_normalization=False,  # divide each input by its std
            zca_whitening=False,  # apply ZCA whitening
            zca_epsilon=1e-06,  # epsilon for ZCA whitening            
            rotation_range=0.,  # randomly rotate images in the range (degrees, 0 to 180)
            width_shift_range=0.,  # randomly shift images horizontally (fraction of total width)
            height_shift_range=0.,  # randomly shift images vertically (fraction of total height)
            brightness_range=None,
            shear_range=0.,  # set range for random shear(Shear angle in counter-clockwise direction in degrees)
            zoom_range=0.,  # set range for random zoom. If a float, `[lower, upper] = [1-zoom_range, 1+zoom_range]`.
            channel_shift_range=0.,  # set range for random channel shifts
            fill_mode='nearest',  # One of {"constant", "nearest", "reflect" or "wrap"}
            cval=0.,  # value used for fill_mode = "constant"
            horizontal_flip=True,  # randomly flip images
            vertical_flip=False,  # randomly flip images
            rescale=None,  # set rescaling factor (applied before any other transformation)
            preprocessing_function=None,  # set function that will be applied on each input
            data_format="channels_last",  # either "channels_first" or "channels_last"
            validation_split=0.0  # fraction of images reserved for validation (strictly between 0 and 1)
        ):
            return ImageDataGenerator(featurewise_center,
                samplewise_center,
                featurewise_std_normalization,
                samplewise_std_normalization,
                zca_whitening,
                zca_epsilon,
                rotation_range,
                width_shift_range,
                height_shift_range,
                brightness_range,
                shear_range,
                zoom_range,
                channel_shift_range,
                fill_mode,
                cval,
                horizontal_flip,
                vertical_flip,
                rescale,
                preprocessing_function,
                data_format,
                validation_split)

    def create_model(self, num_classes):
        print('create_model method should be implemented in each model')
        return None

    def init_output_dictionary_and_model(self, class_indices, num_classes):
        """Initializes self.model.
        
        Arguments:
            class_indices {dict} -- A reversed dictionary of output_dictionary.
            num_classes {int} -- A number of classes to classify.
        """
        self.model = self.create_model( num_classes )
        self.set_output_dictionary( reverse_dict(class_indices) )
        return

    def prepare_train_data(self, get_image_from = 'directory', data_path = None, data_array = None, target_array = None):
        self.get_image_from = get_image_from
        self.data_path = data_path
        if self.get_image_from == 'argument':
            if type(data_array) == type(None) or type(target_array) == type(None):
                raise TypeError('you should prepare arrays to initialize model')
            else:
                return self.reshape_data(data_array), target_array
        elif self.get_image_from != 'directory':
            raise ValueError("value of get_image_from should be either 'directory' or 'argument'.")

    def prepare_y(self, target_array, class_indices, num_classes):
        """Prepares y for a keras model.(ex. y_train)
        
        Arguments:
            target_array {ndarray} -- ndarray. Appropriate outputs of input data.
            class_indices {dict} --
                A dictionary of classes to targets.
                (A reversed dictionary of self.model.output_dictionary)
            num_classes {int} -- A number of the entire classes.
        
        Returns:
            [ndarray] -- A binary matrix representation of the input.
        """
        y_list = list()
        for i in range(target_array.shape[0]):
            label_class = class_indices[target_array[i]]
            y_list.append(label_class)        
        y = keras.utils.to_categorical(numpy.asarray(y_list), num_classes)
        return y

    def reshape_data(self, data_array, cv_interpolation = cv2.INTER_LINEAR):
        """Changes an array of images to fit with model's input.
        Note that this method casts and rescales data to a range of [0, 1].
        
        Arguments:
            data_array {ndarray} -- An array of images.
        
        Keyword Arguments:
            cv_interpolation {int} -- cv2 interpolation. (default: {cv2.INTER_LINEAR})

        Returns:
            [ndarray] -- Reshaped data array.
        """
        if data_array.shape[1:] != self.input_shape:
            reshaped_list = list()
            for i in range(data_array.shape[0]):
                resized_img = cv2.resize(data_array[i], (self.input_shape[0], self.input_shape[1]), interpolation = cv_interpolation)
                reshaped_list.append(resized_img)
            data_array = numpy.asarray(reshaped_list)
            reshaped_list = [] # empty list after use
        data_array = data_array.astype('float32')
        data_array /= 255
        return data_array

    def train(self,
            x_train = None,
            target_array = None,
            optimizer = 'nadam',
            metrics = ['accuracy'],
            image_data_generator = None,
            batch_size = 32,
            steps_per_epoch = None,
            epochs = 1,
            verbose = 1,
            callbacks = None,
            shuffle = True,
            use_fit_generator = False
        ):
        """Trains an application.
        This method automatically checks an existence of self.model.
        If it does not exist, this method will initialize an application based on information of train data.
        (ex. number of unique classes in the target_array or directory)
        
        Keyword Arguments:
            x_train {numpy array or None} --
                Numpy array of train images. (default: {None})
            target_array {numpy array or None} --
                Numpy array of answer label. (default: {None})
            optimizer {str or keras optimizer instance} --
                See https://keras.io/optimizers/ for more information about optimizers. (default: {'nadam'})
            metrics {list} --
                List of metrics to be evaluated by the application during training and evaluating(testing). (default: {['accuracy']})
            image_data_generator {ImageDataGenerator} --
                A class which is the same as keras.preprocessing.image.ImageDataGenerator.
                If you know how to use keras, you can set this argument.
                Otherwise, Just forget about this one.
                (default: {None})
            batch_size {int} --
                Number of samples per gradient update.
                If unspecified, batch_size will default to 32.
                If you don't know about batch size,
                just adjust this value to reduce a training time.
                (default: {32})
            steps_per_epoch {int or None} -- Total number of steps (batches of samples) before declaring one epoch finished. (default: {None})
            epochs {int} -- Number of epochs to train the application. (default: {1})
            verbose {int} -- Verbosity mode. 0 = silent, 1 = progress bar, 2 = one line per epoch. (default: {1})
            callbacks {[type]} --
                List of keras.callbacks.Callback instances.
                If you don't know, then you don't have to use this.
                (default: {None})
            shuffle {bool} -- Has no effect when steps_per_epoch is not None. (default: {True})
            use_fit_generator {bool} --
                Decide whether using keras's fit_generator or not when the data are images.
                Check https://keras.io/models/model/ for usage.
                If you don't want to know how to use this, then just forget it.
                (default: {False})
        """
        if use_fit_generator == False:
            if self.get_image_from == 'directory':
                x_train, target_array = directory_images_to_arrays(self.data_path, self.input_shape[:2])
            if type(self.model) == type(None):
                unique_classes = numpy.lib.arraysetops.unique(target_array)
                class_indices = self.create_class_indices(unique_classes)
                num_classes = len(class_indices)
                self.init_output_dictionary_and_model(class_indices, num_classes)
                self.compile_model(optimizer = optimizer, loss = keras.losses.categorical_crossentropy, metrics = metrics)
            else:
                num_classes = self.model.output_shape[1]
            y_train = self.prepare_y(target_array, reverse_dict(self.model.output_dictionary), num_classes)
            self.model.fit(x_train, y_train, batch_size = batch_size, steps_per_epoch=steps_per_epoch, epochs=epochs, verbose=verbose, callbacks=callbacks, shuffle=shuffle)
        else:
            if type(image_data_generator) == type(None):
                if self.get_image_from == 'directory':
                    train_datagen = self.create_image_data_generator(rescale = 1./255)
                else:
                    train_datagen = self.create_image_data_generator()
            else:
                train_datagen = image_data_generator
            if self.get_image_from == 'directory':
                train_generator = train_datagen.flow_from_directory(self.data_path, target_size = self.input_shape[:2], class_mode = 'categorical', batch_size = batch_size)
                if type(self.model) == type(None):
                    class_indices = train_generator.class_indices
                    self.init_output_dictionary_and_model(class_indices, len(class_indices))
                    self.compile_model(optimizer = optimizer, loss = keras.losses.categorical_crossentropy, metrics = metrics)
                self.model.fit_generator(train_generator, steps_per_epoch=steps_per_epoch, epochs=epochs, verbose=verbose, callbacks=callbacks, shuffle=shuffle)
            elif self.get_image_from == 'argument':
                if type(self.model) == type(None):
                    unique_classes = numpy.lib.arraysetops.unique(target_array)
                    class_indices = self.create_class_indices(unique_classes)
                    num_classes = len(class_indices)
                    self.init_output_dictionary_and_model(class_indices, num_classes)
                    self.compile_model(optimizer = optimizer, loss = keras.losses.categorical_crossentropy, metrics = metrics)
                else:
                    num_classes = self.model.output_shape[1]
                y_train = self.prepare_y(target_array, reverse_dict(self.model.output_dictionary), num_classes)
                train_generator = train_datagen.flow(x_train, y_train, batch_size = batch_size)
                self.model.fit_generator(train_generator, steps_per_epoch=steps_per_epoch, epochs=epochs, verbose=verbose, callbacks=callbacks, shuffle=shuffle)
