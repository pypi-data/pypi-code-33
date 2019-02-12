from keras.models import load_model

import numpy


class Application:
    
    def __init__(self, model_path = None):
        """Initializes a neural network application.

        If you want to load an application you've already trained, just give a path of application file.
        
        Keyword Arguments:
            model_path {str} -- A path of application file. (default: {None})
        
        Raises:
            e -- Raises error when loading an application is failed.
        """
        if type(model_path) == type(None):
            self.model = None
        else:
            try:
                self.model = load_model(model_path)
                self.input_shape = self.model.input_shape[1:]
                if type(self.model) == type(None):
                    print('Nothing loaded')
            except Exception as e:
                print('Model loading failed')
                raise e

    def compile_model(self, optimizer, loss=None, metrics=['accuracy']):
        """This function compiles self.model according to arguments.
        
        Arguments:
            optimizer {str or keras optimizer instance} -- See https://keras.io/optimizers/ for more information about optimizers.
        
        Keyword Arguments:
            loss {str or objective function} -- See https://keras.io/losses/ for more information about loss. (default: {None})
            metrics {list} -- List of metrics to be evaluated by the application during training and evaluating(testing). (default: {['accuracy']})
        """
        self.model.compile(optimizer, loss=loss, metrics=metrics)  

    def evaluate(self, data_array, target_array, batch_size = 32, verbose = 1, sample_weight = None, steps = None):
        """Returns the loss value & metrics values for the application in test mode.
       
        Arguments:
            data_array {ndarray} -- The input data like x_test of keras.
            target_array {ndarray} -- Appropriate outputs of data_array.
        
        Keyword Arguments:
            batch_size {int} -- Number of samples per evaluation step. (default: {32})
            verbose {int} -- Verbosity mode. 0 = silent, 1 = progress bar. (default: {1})
            sample_weight {ndarray or None} --
                Optional Numpy array of weights for the test samples, used for weighting the loss function.
                Check https://keras.io/models/model/ for more information about sample_weight.
                (default: {None})
            steps {int or None} --
                Total number of steps (batches of samples) before declaring the evaluation round finished.
                Ignored with the default value of None.
                (default: {None})
        """
        evaluation_result = self.model.evaluate(data_array, target_array, batch_size = batch_size, verbose = verbose, sample_weight = sample_weight, steps = steps)
        return evaluation_result

    def predict(self, data_array, predict_classes = True, batch_size = 32, verbose = 0, steps = None):
        """Generates output of predictions for the input samples.
        
        Arguments:
            data_array {ndarray} -- The input data like x_test of keras.
        
        Keyword Arguments:
            predict_classes {bool} --
                Decides a prediction result's type.
                By default, a return value of prediction result is an array of classes.
                If you set predict_classes as False, you can get a raw output array as a prediction result.
                (default: {True})
            batch_size {int} -- Number of samples per prediction. (default: {32})
            verbose {int} -- Verbosity mode, 0 or 1.(default: {0})
            steps {int or None} --
                Total number of steps (batches of samples) before declaring the prediction round finished.
                Ignored with the default value of None.
                (default: {None})

        Raises:
            e -- Raise exception when prediction failed.
        
        Returns:
            [ndarray] -- Predicted classes(labels) of input data
        """
        try:
            probs = self.model.predict(data_array, batch_size = batch_size, verbose = verbose, steps = steps)
            if predict_classes == False:
                return probs
            predicted_classes = probs.argmax(axis=-1)
            try:
                for i in range(predicted_classes.shape[0]):
                    if i == 0:
                        return_list = [ self.model.output_dictionary[predicted_classes[i]] ]
                    else:
                        return_list.append( self.model.output_dictionary[predicted_classes[i]] )
                return numpy.asarray(return_list)
            except:
                return predicted_classes
        except Exception as e:
            # Prediction failed
            raise e

    def print_summary(self):
        self.model.summary()

    def save(self, model_path):
        """Saves an application as h5 format.
        
        Arguments:
            model_path {str} -- Path to save application.
                
        Raises:
            TypeError -- Raises error if self.model is not created.
            e -- Raises error if a path is wrong.
        """
        try:
            if type(self.model) == type(None):
                raise TypeError('you should create an application before save it')
            self.model.save(model_path)
        except Exception as e:
            raise e

    def set_output_dictionary(self, output_dictionary):
        self.model.output_dictionary = output_dictionary
        self.model.__class__.output_dictionary = self.model.output_dictionary 
