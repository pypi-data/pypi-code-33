from ftk.models.deep_models.deep_forecaster import DeepForecaster

from keras.layers import Dense, Flatten
from keras.models import Input, Model
from keras.regularizers import l1


class DeepLinearForecaster(DeepForecaster):
    """
    Class that performs l1 regularized linear regression using Keras 
    archetecture.

    :param l1_penalty: The penalty for l1 regularization
    :type l1_penalty: float between 0 and 1
    """

    def __init__(self, lag_window_size, horizon,
                 preprocess=None, post_process=None, l1_penalty=0.):
        super(DeepLinearForecaster, self).__init__(lag_window_size, horizon,
                                                   preprocess=preprocess, 
                                                   post_process=post_process)
        # Example of a model specific parameter
        self.l1_penalty = l1_penalty

    def _create_estimator_(self, n_features):
        input_layer = Input(name='input_layer', shape=(
            self.lag_window_size, n_features, ))
        x = Flatten()(input_layer)
        # Note self.l1_penalty is used to parameterize the model
        output_layer = Dense(self.horizon, activation='linear',
                             kernel_regularizer=l1(self.l1_penalty))(x)
        model = Model(input_layer, output_layer)
        self._estimator = model
