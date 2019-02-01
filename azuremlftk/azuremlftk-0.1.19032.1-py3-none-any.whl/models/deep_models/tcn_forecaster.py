import keras.backend as K
from keras.layers import Conv1D, SpatialDropout1D, BatchNormalization
from keras.layers import Activation, Lambda, Add, Subtract, Multiply
from keras.layers import Convolution1D, Dense, ZeroPadding1D
from keras.models import Input, Model
import keras.layers

from ftk.models.deep_models.deep_forecaster import DeepForecaster


class TCNForecaster(DeepForecaster):
    """
    Class that implements the Lea et al. 2016 paper "Temporal Convolutional Networks: 
    A Unified Approach to Action Segmentation"

    :param nb_filters: The number of filters to use in the convolutional layers.
    :type nb_filters: int

    :param kernel_size: The size of the kernel to use in each convolutional layer.
    :type kernel_size: int

    :param dilations: The list of the dilations. Example is: [1, 2, 4, 8, 16, 32, 64].
    :type dilations: list of ints

    :param nb_stacks: The number of stacks of residual blocks to use.
    :type nb_stacks: int

    :param activation: The activations to use.
    :type activation: str

    :param use_skip_connections: 
        Whether we want to add skip connections from input to each residual block.
    :type use_skip_connections: logical

    :param dropout_rate: Fraction of the input units to drop.
    :type dropout_rate: float between 0 and 1

    :param post_process: Whether to add the last observed value to the output.
    :type post_process: logical
    """

    def __init__(self, lag_window_size, horizon, nb_filters=24,
                 kernel_size=8, dilations=[1, 2, 4, 8], nb_stacks=8,
                 activation='norm_relu', use_skip_connections=False,
                 output_slice_index='last', dropout_rate=0.5,
                 post_process=None, preprocess=None):

        super(TCNForecaster, self).__init__(lag_window_size, horizon)

        self.nb_filters = nb_filters
        self.kernel_size = kernel_size
        self.dilations = dilations
        self.nb_stacks = nb_stacks
        self.activation = activation
        self.use_skip_connections = use_skip_connections
        self.output_slice_index = output_slice_index
        self.dropout_rate = dropout_rate
        self.post_process = post_process
        self.preprocess = preprocess

    def channel_normalization(self, x):
        # Normalize by the highest activation
        max_values = K.max(K.abs(x), 2, keepdims=True) + 1e-5
        out = x / max_values
        return out

    def extract_mean_value(self, x):
        # Normalize by the highest activation
        mean_value = Lambda(lambda x: K.mean(
            K.abs(x), 1, keepdims=True) + 1e-5, name='mean_value')(x)
        mean_target = Lambda(
            lambda tt: tt[:, :, 0], name='select_value')(mean_value)
        mean_target = Lambda(lambda x: K.repeat_elements(
            x, self.horizon, 1), name='repeat')(mean_target)
        mean_value = Lambda(lambda x: K.repeat_elements(
            x, self.lag_window_size, 1), name='repeat')(mean_value)
        return mean_value, mean_target

    def extract_last_value(self, x):
        last_value = Lambda(lambda tt: tt[:, -1, 0], name='select_value')(x)
        last_value = Lambda(K.expand_dims, name='add_dim')(last_value)
        last_value = Lambda(lambda x: K.repeat_elements(
            x, self.horizon, -1), name='repeat')(last_value)
        return last_value

    def difference_series(self, x):
        difference = ZeroPadding1D((1, 0))(Lambda(lambda x: x[:, :-1, :])(x))
        x = Subtract()([x, difference])
        return x

    def wave_net_activation(self, x):
        tanh_out = Activation('tanh')(x)
        sigm_out = Activation('sigmoid')(x)
        return keras.layers.multiply([tanh_out, sigm_out])

    def residual_block(self, x, s, i):
        original_x = x
        conv = Conv1D(filters=self.nb_filters, kernel_size=self.kernel_size,
                      dilation_rate=2 ** i, padding='causal',
                      name='dilated_conv_%d_tanh_s%d' % (2 ** i, s))(x)
        if self.activation == 'norm_relu':
            x = Activation('relu')(conv)
            x = Lambda(self.channel_normalization)(x)
        elif self.activation == 'wavenet':
            x = self.wave_net_activation(conv)
        else:
            x = Activation(self.activation)(conv)

        x = SpatialDropout1D(self.dropout_rate)(x)
        x = BatchNormalization()(x)

        # 1x1 conv.
        x = Convolution1D(self.nb_filters, 1, padding='same')(x)
        res_x = keras.layers.add([original_x, x])
        return res_x, x

    def _create_estimator_(self, n_features):
        input_layer = Input(name='input_layer', shape=(
            self.lag_window_size, n_features, ))

        if self.post_process == 'subtract':
            last_value = self.extract_last_value(input_layer)
        if self.post_process == 'multiply' or self.preprocess == 'divide':
            mean_value, mean_target = self.extract_mean_value(lag_input_layer)

        x = input_layer
        if self.preprocess == 'difference':
            x = self.difference_series(x)
        if self.preprocess == 'subtract':
            x = Lambda(lambda x: x - mean_value)(x)
        if self.preprocess == 'divide':
            x = Lambda(lambda x: x/mean_value)(x)

        x = Convolution1D(self.nb_filters, self.kernel_size,
                          padding='causal', name='initial_conv')(x)

        skip_connections = []
        for s in range(self.nb_stacks):
            for i in self.dilations:
                x, skip_out = self.residual_block(x, s, i)
                skip_connections.append(skip_out)

        if self.use_skip_connections:
            x = keras.layers.add(skip_connections)
        x = Activation('relu')(x)

        if self.output_slice_index is not None:  # can test with 0 or -1.
            if self.output_slice_index == 'last':
                self.output_slice_index = -1
            if self.output_slice_index == 'first':
                self.output_slice_index = 0
            x = Lambda(lambda tt: tt[:, self.output_slice_index, :])(x)

        print('x.shape=', x.shape)

        x = Dense(self.horizon)(x)
        x = Activation('linear', name='output_dense')(x)
        if self.post_process == 'subtract':
            x = Add()([x, last_value])
        elif self.post_process == 'multiply':
            x = Multiply()([x, mean_value])
        output_layer = x

        model = Model(input_layer, output_layer)

        self._estimator = model
