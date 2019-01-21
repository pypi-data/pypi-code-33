from __future__ import absolute_import

from keras import activations, initializers, regularizers, constraints
from keras import backend as K
from keras.layers import Layer, LeakyReLU, Dropout, AveragePooling2D, AveragePooling1D


class GraphConv(Layer):
    """
    A graph convolutional layer as presented by [Kipf & Welling (2016)](https://arxiv.org/abs/1609.02907).

    **Mode**: single, mixed, batch.
    
    This layer computes the transformation:
    $$  
        Z = \\sigma(AXW + b)
    $$
    where \(X\) is the node features matrix, \(A\) is the normalized Laplacian,
    \(W\) is the convolution kernel, \(b\) is a bias vector, and \(\\sigma\) is 
    the activation function.
    
    **Input**
    
    - node features of shape `(batch, num_nodes, num_features)`, depending on the
    mode;
    - Laplacians of shape `(batch, num_nodes, num_nodes)`, depending on the mode.
    The Laplacians can be computed from the adjacency matrices like in the
    original paper using `utils.convolution.localpooling_filter`.
    
    **Output**
    
    - node features with the same shape of the input, but the last dimension
    changed to `channels`.
        
    **Arguments**
    
    - `channels`: integer, number of output channels;
    - `activation`: activation function to use;
    - `use_bias`: whether to add a bias to the linear transformation;
    - `kernel_initializer`: initializer for the kernel matrix;
    - `bias_initializer`: initializer for the bias vector;
    - `kernel_regularizer`: regularization applied to the kernel matrix;  
    - `bias_regularizer`: regularization applied to the bias vector;
    - `activity_regularizer`: regularization applied to the output;
    - `kernel_constraint`: constraint applied to the kernel matrix;
    - `bias_constraint`: constraint applied to the bias vector.
    
    **Usage**  
    
    ```py
    fltr = localpooling_filter(adj)  # Can be any pre-processing
    ...
    X = Input(shape=(num_nodes, num_features))
    filter = Input((num_nodes, num_nodes))
    Z = GraphConv(units, activation='relu')([X, filter])
    ...
    model.fit([node_features, fltr], y)
    ```
    """
    def __init__(self,
                 channels,
                 activation=None,
                 use_bias=True,
                 kernel_initializer='glorot_uniform',
                 bias_initializer='zeros',
                 kernel_regularizer=None,
                 bias_regularizer=None,
                 activity_regularizer=None,
                 kernel_constraint=None,
                 bias_constraint=None,
                 **kwargs):
        if 'input_shape' not in kwargs and 'input_dim' in kwargs:
            kwargs['input_shape'] = (kwargs.pop('input_dim'),)
        super(GraphConv, self).__init__(**kwargs)
        self.channels = channels
        self.activation = activations.get(activation)
        self.use_bias = use_bias
        self.kernel_initializer = initializers.get(kernel_initializer)
        self.bias_initializer = initializers.get(bias_initializer)
        self.kernel_regularizer = regularizers.get(kernel_regularizer)
        self.bias_regularizer = regularizers.get(bias_regularizer)
        self.activity_regularizer = regularizers.get(activity_regularizer)
        self.kernel_constraint = constraints.get(kernel_constraint)
        self.bias_constraint = constraints.get(bias_constraint)
        self.supports_masking = False

    def build(self, input_shape):
        assert len(input_shape) >= 2
        input_dim = input_shape[0][-1]
        self.kernel = self.add_weight(shape=(input_dim, self.channels),
                                      initializer=self.kernel_initializer,
                                      name='kernel',
                                      regularizer=self.kernel_regularizer,
                                      constraint=self.kernel_constraint)
        if self.use_bias:
            self.bias = self.add_weight(shape=(self.channels,),
                                        initializer=self.bias_initializer,
                                        name='bias',
                                        regularizer=self.bias_regularizer,
                                        constraint=self.bias_constraint)
        else:
            self.bias = None
        self.built = True

    def call(self, inputs):
        features = inputs[0]
        fltr = inputs[1]

        # Convolution
        output = K.dot(features, self.kernel)
        if len(K.int_shape(features)) == 2:
            # Single mode
            output = K.dot(fltr, output)
        else:
            if len(K.int_shape(fltr)) == 3:
                # Batch mode
                output = K.batch_dot(fltr, output)
            else:
                # Mixed mode
                output = K.tf.einsum('ij,bjk->bik', fltr, output)  # TODO implement in pure Keras

        if self.use_bias:
            output = K.bias_add(output, self.bias)
        if self.activation is not None:
            output = self.activation(output)
        return output

    def compute_output_shape(self, input_shape):
        features_shape = input_shape[0]
        output_shape = features_shape[:-1] + (self.channels,)
        return output_shape

    def get_config(self):
        config = {
            'units': self.channels,
            'activation': activations.serialize(self.activation),
            'use_bias': self.use_bias,
            'kernel_initializer': initializers.serialize(self.kernel_initializer),
            'bias_initializer': initializers.serialize(self.bias_initializer),
            'kernel_regularizer': regularizers.serialize(self.kernel_regularizer),
            'bias_regularizer': regularizers.serialize(self.bias_regularizer),
            'activity_regularizer': regularizers.serialize(self.activity_regularizer),
            'kernel_constraint': constraints.serialize(self.kernel_constraint),
            'bias_constraint': constraints.serialize(self.bias_constraint)
        }
        base_config = super(GraphConv, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))


class ChebConv(Layer):
    """
    A Chebyshev convolutional layer as presented by [Defferrard et al. (2016)](https://arxiv.org/abs/1606.09375).

    **Mode**: single, mixed, batch.
    
    Given a list of Chebyshev polynomials \(T = [T_{1}, ..., T_{K}]\), 
    this layer computes the transformation:
    $$
        Z = \\sigma( \\sum \\limits_{k=1}^{K} T_{k} X W  + b)
    $$
    where \(X\) is the node features matrix, \(W\) is the convolution kernel, 
    \(b\) is the bias vector, and \(\sigma\) is the activation function.

    **Input**

    - node features of shape `(batch, num_nodes, num_features)`, depending on the
    mode;
    - a list of Chebyshev filters of shape `(batch, num_nodes, num_nodes)`,
    depending on the mode.
    The filters can be generated from the adjacency matrices using
    `utils.convolution.chebyshev_filter`.

    **Output**

    - node features with the same shape of the input, but the last dimension
    changed to `channels`.
    
    **Arguments**
    
    - `channels`: integer, number of output channels;
    - `activation`: activation function to use;
    - `use_bias`: boolean, whether to add a bias to the linear transformation;
    - `kernel_initializer`: initializer for the kernel matrix;
    - `bias_initializer`: initializer for the bias vector;
    - `kernel_regularizer`: regularization applied to the kernel matrix;  
    - `bias_regularizer`: regularization applied to the bias vector;
    - `activity_regularizer`: regularization applied to the output;
    - `kernel_constraint`: constraint applied to the kernel matrix;
    - `bias_constraint`: constraint applied to the bias vector.
    
    **Usage**
    ```py
    fltr = chebyshev_filter(adj, K)
    ...
    X = Input(shape=(num_nodes, num_features))
    filter = Input((num_nodes, num_nodes))
    Z = GraphConv(units, activation='relu')([X, filter])
    ...
    model.fit([node_features, fltr], y)
    ```
    """
    def __init__(self,
                 channels,
                 activation=None,
                 use_bias=True,
                 kernel_initializer='glorot_uniform',
                 bias_initializer='zeros',
                 kernel_regularizer=None,
                 bias_regularizer=None,
                 activity_regularizer=None,
                 kernel_constraint=None,
                 bias_constraint=None,
                 **kwargs):
        if 'input_shape' not in kwargs and 'input_dim' in kwargs:
            kwargs['input_shape'] = (kwargs.pop('input_dim'),)
        super(ChebConv, self).__init__(**kwargs)
        self.channels = channels
        self.activation = activations.get(activation)
        self.use_bias = use_bias
        self.kernel_initializer = initializers.get(kernel_initializer)
        self.bias_initializer = initializers.get(bias_initializer)
        self.kernel_regularizer = regularizers.get(kernel_regularizer)
        self.bias_regularizer = regularizers.get(bias_regularizer)
        self.activity_regularizer = regularizers.get(activity_regularizer)
        self.kernel_constraint = constraints.get(kernel_constraint)
        self.bias_constraint = constraints.get(bias_constraint)
        self.supports_masking = False

    def build(self, input_shape):
        assert len(input_shape) >= 2
        input_dim = input_shape[0][-1]
        support_len = len(input_shape) - 1
        self.kernel = self.add_weight(shape=(input_dim * support_len, self.channels),
                                      initializer=self.kernel_initializer,
                                      name='kernel',
                                      regularizer=self.kernel_regularizer,
                                      constraint=self.kernel_constraint)
        if self.use_bias:
            self.bias = self.add_weight(shape=(self.channels,),
                                        initializer=self.bias_initializer,
                                        name='bias',
                                        regularizer=self.bias_regularizer,
                                        constraint=self.bias_constraint)
        else:
            self.bias = None
        self.built = True

    def call(self, inputs):
        features = inputs[0]
        fltr_list = inputs[1:]

        # Convolution
        supports = list()
        for fltr in fltr_list:
            if len(K.int_shape(features)) == 2:
                # Single mode
                s = K.dot(fltr, features)
            else:
                if len(K.int_shape(fltr)) == 3:
                    # Batch mode
                    s = K.batch_dot(fltr, features)
                else:
                    # Mixed mode
                    s = K.tf.einsum('ij,bjk->bik', fltr, features)  # TODO implement in pure Keras
            supports.append(s)
        supports = K.concatenate(supports, axis=-1)
        output = K.dot(supports, self.kernel)

        if self.use_bias:
            output = K.bias_add(output, self.bias)
        if self.activation is not None:
            output = self.activation(output)
        return output

    def compute_output_shape(self, input_shape):
        features_shape = input_shape[0]
        output_shape = features_shape[:-1] + (self.channels,)
        return output_shape

    def get_config(self):
        config = {
            'channels': self.channels,
            'activation': activations.serialize(self.activation),
            'use_bias': self.use_bias,
            'kernel_initializer': initializers.serialize(self.kernel_initializer),
            'bias_initializer': initializers.serialize(self.bias_initializer),
            'kernel_regularizer': regularizers.serialize(self.kernel_regularizer),
            'bias_regularizer': regularizers.serialize(self.bias_regularizer),
            'activity_regularizer': regularizers.serialize(self.activity_regularizer),
            'kernel_constraint': constraints.serialize(self.kernel_constraint),
            'bias_constraint': constraints.serialize(self.bias_constraint)
        }
        base_config = super(ChebConv, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))


class EdgeConditionedConv(Layer):
    """
    An edge-conditioned convolutional layer as presented by [Simonovsky and
    Komodakis (2017)](https://arxiv.org/abs/1704.02901).

    **Mode**: batch.
    
    This layer computes a transformation of the input \(X\), s.t. for each node
    \(i\) we have:
    $$
        X^{out}_i =  \\frac{1}{\\mathcal{N}(i)} \\sum\\limits_{j \\in \\mathcal{N}(i)} F(E_{ji}) X_{j} + b
    $$
    where \(\\mathcal{N}(i)\) represents the one-step neighbourhood of node \(i\),
     \(F\) is a neural network that outputs the convolution kernel as a
    function of edge attributes, \(E\) is the edge attributes matrix, and \(b\)
    is a bias vector.

    **Input**

    - node features of shape `(batch, num_nodes, num_node_features)`, depending
    on the mode;
    - adjacency matrices of shape `(batch, num_nodes, num_nodes)`, depending on
    the mode.
    - edge features of shape `(batch, num_nodes, num_nodes, num_edge_features)`,
    depending on the mode.

    **Output**

    - node features with the same shape of the input, but the last dimension
    changed to `channels`.
    
    **Arguments**
    
    - `channels`: integer, number of output channels;
    - `num_nodes`: integer, the number of nodes in the graphs;
    - `edge_features_dim`: the dimension of the edge features;
    - `kernel_network`: a list of integers describing the hidden structure of
    the kernel-generating network (i.e., the ReLU layers before the linear
    output);
    - `activation`: activation function to use;
    - `use_bias`: boolean, whether to add a bias to the linear transformation;
    - `kernel_initializer`: initializer for the kernel matrix;
    - `bias_initializer`: initializer for the bias vector;
    - `kernel_regularizer`: regularization applied to the kernel matrix;  
    - `bias_regularizer`: regularization applied to the bias vector;
    - `activity_regularizer`: regularization applied to the output;
    - `kernel_constraint`: constraint applied to the kernel matrix;
    - `bias_constraint`: constraint applied to the bias vector.
    
    **Usage**
    ```py
    adj = add_eye_batch(adj)
    ...
    nf = Input(shape=(num_nodes, num_node_features))
    a = Input(shape=(num_nodes, num_nodes))
    ef = Input(shape=(num_nodes, num_nodes, num_edge_features))
    Z = EdgeConditionedConv(32, num_nodes, num_edge_features)([nf, a, ef])
    ...
    model.fit([node_features, adj, edge_features], y)
    ```
    """
    # TODO: mixed, batch
    def __init__(self,
                 channels,
                 kernel_network=None,
                 activation=None,
                 use_bias=True,
                 kernel_initializer='glorot_uniform',
                 bias_initializer='zeros',
                 kernel_regularizer=None,
                 bias_regularizer=None,
                 activity_regularizer=None,
                 kernel_constraint=None,
                 bias_constraint=None,
                 **kwargs):
        if 'input_shape' not in kwargs and 'input_dim' in kwargs:
            kwargs['input_shape'] = (kwargs.pop('input_dim'),)
        super(EdgeConditionedConv, self).__init__(**kwargs)
        self.channels = channels
        self.kernel_network = kernel_network
        self.activation = activations.get(activation)
        self.use_bias = use_bias
        self.kernel_initializer = initializers.get(kernel_initializer)
        self.bias_initializer = initializers.get(bias_initializer)
        self.kernel_regularizer = regularizers.get(kernel_regularizer)
        self.bias_regularizer = regularizers.get(bias_regularizer)
        self.activity_regularizer = regularizers.get(activity_regularizer)
        self.kernel_constraint = constraints.get(kernel_constraint)
        self.bias_constraint = constraints.get(bias_constraint)
        self.supports_masking = False

    def build(self, input_shape):
        assert len(input_shape) >= 2
        if self.use_bias:
            self.bias = self.add_weight(shape=(self.channels,),
                                        initializer=self.bias_initializer,
                                        name='bias',
                                        regularizer=self.bias_regularizer,
                                        constraint=self.bias_constraint)
        else:
            self.bias = None
        self.built = True

    def call(self, inputs):
        node_features = inputs[0]  # (batch_size, N, F)
        fltr = inputs[1]           # (batch_size, N, N)
        edge_features = inputs[2]  # (batch_size, N, N, S)

        # Parameters
        F = K.int_shape(node_features)[-1]
        F_ = self.channels

        # Normalize adjacency matrix
        fltr = fltr / K.maximum(K.sum(fltr, axis=-1, keepdims=True), 10e-12)

        # Filter network
        kernel_network = edge_features
        if self.kernel_network is not None:
            for i, l in enumerate(self.kernel_network):
                kernel_network = self.dense_layer(kernel_network, l,
                                                  'FGN_{}'.format(i),
                                                  activation='relu',
                                                  use_bias=self.use_bias,
                                                  kernel_initializer=self.kernel_initializer,
                                                  bias_initializer=self.bias_initializer,
                                                  kernel_regularizer=self.kernel_regularizer,
                                                  bias_regularizer=self.bias_regularizer,
                                                  kernel_constraint=self.kernel_constraint,
                                                  bias_constraint=self.bias_constraint)
        kernel_network = self.dense_layer(kernel_network, F_ * F, 'FGN_out')

        # Convolution
        target_shape = (-1,) + K.int_shape(kernel_network)[1:-1] + (F_, F)
        kernel = K.reshape(kernel_network, target_shape)
        output = kernel * fltr[..., None, None]
        output = K.tf.einsum('abicf,aif->abc', output, node_features)  # TODO remove tf dependency

        if self.use_bias:
            output = K.bias_add(output, self.bias)
        if self.activation is not None:
            output = self.activation(output)

        return output

    def compute_output_shape(self, input_shape):
        features_shape = input_shape[0]
        output_shape = features_shape[:-1] + (self.channels,)
        return output_shape

    def get_config(self):
        config = {
            'channels': self.channels,
            'activation': activations.serialize(self.activation),
            'use_bias': self.use_bias,
            'kernel_initializer': initializers.serialize(self.kernel_initializer),
            'bias_initializer': initializers.serialize(self.bias_initializer),
            'kernel_regularizer': regularizers.serialize(self.kernel_regularizer),
            'bias_regularizer': regularizers.serialize(self.bias_regularizer),
            'activity_regularizer': regularizers.serialize(self.activity_regularizer),
            'kernel_constraint': constraints.serialize(self.kernel_constraint),
            'bias_constraint': constraints.serialize(self.bias_constraint)
        }
        base_config = super(EdgeConditionedConv, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))

    def dense_layer(self,
                    x,
                    units,
                    name,
                    activation=None,
                    use_bias=True,
                    kernel_initializer='glorot_uniform',
                    bias_initializer='zeros',
                    kernel_regularizer=None,
                    bias_regularizer=None,
                    kernel_constraint=None,
                    bias_constraint=None):
        input_dim = K.int_shape(x)[-1]
        kernel = self.add_weight(shape=(input_dim, units),
                                 name=name + '_kernel',
                                 initializer=kernel_initializer,
                                 regularizer=kernel_regularizer,
                                 constraint=kernel_constraint)
        bias = self.add_weight(shape=(units,),
                               name=name + '_bias',
                               initializer=bias_initializer,
                               regularizer=bias_regularizer,
                               constraint=bias_constraint)
        act = activations.get(activation)
        output = K.dot(x, kernel)
        if use_bias:
            output = K.bias_add(output, bias)
        output = act(output)
        return output


class GraphAttention(Layer):
    """
    A graph attention layer as presented by
    [Velickovic et al. (2017)](https://arxiv.org/abs/1710.10903).

    **Mode**: single.
    
    This layer computes the a convolution similar to `layers.GraphConv`, but
    uses the attention mechanism to weight the adjacency matrix instead of
    using the normalized Laplacian.

    **Input**

    - node features of shape `(num_nodes, num_features)`;
    - adjacency matrices of shape `(num_nodes, num_nodes)`;

    **Output**

    - node features with the same shape of the input, but the last dimension
    changed to `channels`.
    
    **Arguments**
    
    - `channels`: integer, number of output channels;
    - `attn_heads`: number of attention heads to use;
    - `attn_heads_reduction`: how to reduce the outputs of the attention heads 
    (can be either 'concat' or 'average');
    - `dropout_rate`: internal dropout rate;
    - `activation`: activation function to use;
    - `use_bias`: boolean, whether to add a bias to the linear transformation;
    - `kernel_initializer`: initializer for the kernel matrix;
    - `attn_kernel_initializer`: initializer for the attention kernel matrices;
    - `bias_initializer`: initializer for the bias vector;
    - `kernel_regularizer`: regularization applied to the kernel matrix;  
    - `attn_kernel_regularizer`: regularization applied to the attention kernel 
    matrices;
    - `bias_regularizer`: regularization applied to the bias vector;
    - `activity_regularizer`: regularization applied to the output;
    - `kernel_constraint`: constraint applied to the kernel matrix;
    - `attn_kernel_constraint`: constraint applied to the attention kernel
    matrices;
    - `bias_constraint`: constraint applied to the bias vector.
    
    **Usage**
    ```py
    adj = normalize_sum_to_unity(adj)
    ...
    X = Input(shape=(num_nodes, num_features))
    A = Input((num_nodes, num_nodes))
    Z = GraphAttention(channels, activation='relu')([X, A])
    ...
    model.fit([node_features, fltr], y)
    ```
    """
    # TODO: mixed, batch
    def __init__(self,
                 channels,
                 attn_heads=1,
                 attn_heads_reduction='concat',  # {'concat', 'average'}
                 dropout_rate=0.5,
                 activation='relu',
                 use_bias=True,
                 kernel_initializer='glorot_uniform',
                 bias_initializer='zeros',
                 attn_kernel_initializer='glorot_uniform',
                 kernel_regularizer=None,
                 bias_regularizer=None,
                 attn_kernel_regularizer=None,
                 activity_regularizer=None,
                 kernel_constraint=None,
                 bias_constraint=None,
                 attn_kernel_constraint=None,
                 **kwargs):
        if attn_heads_reduction not in {'concat', 'average'}:
            raise ValueError('Possbile reduction methods: concat, average')

        self.channels = channels
        self.attn_heads = attn_heads
        self.attn_heads_reduction = attn_heads_reduction
        self.dropout_rate = dropout_rate
        self.activation = activations.get(activation)
        self.use_bias = use_bias

        self.kernel_initializer = initializers.get(kernel_initializer)
        self.bias_initializer = initializers.get(bias_initializer)
        self.attn_kernel_initializer = initializers.get(attn_kernel_initializer)

        self.kernel_regularizer = regularizers.get(kernel_regularizer)
        self.bias_regularizer = regularizers.get(bias_regularizer)
        self.attn_kernel_regularizer = regularizers.get(attn_kernel_regularizer)
        self.activity_regularizer = regularizers.get(activity_regularizer)

        self.kernel_constraint = constraints.get(kernel_constraint)
        self.bias_constraint = constraints.get(bias_constraint)
        self.attn_kernel_constraint = constraints.get(attn_kernel_constraint)
        self.supports_masking = False

        # Populated by build()
        self.kernels = []       # Layer kernels for attention heads
        self.biases = []        # Layer biases for attention heads
        self.attn_kernels = []  # Attention kernels for attention heads

        if attn_heads_reduction == 'concat':
            # Output will have shape (..., attention_heads * channels)
            self.output_dim = self.channels * self.attn_heads
        else:
            # Output will have shape (..., channels)
            self.output_dim = self.channels

        super(GraphAttention, self).__init__(**kwargs)

    def build(self, input_shape):
        assert len(input_shape) >= 2
        input_dim = input_shape[0][-1]

        # Initialize weights for each attention head
        for head in range(self.attn_heads):
            # Layer kernel
            kernel = self.add_weight(shape=(input_dim, self.channels),
                                     initializer=self.kernel_initializer,
                                     regularizer=self.kernel_regularizer,
                                     constraint=self.kernel_constraint,
                                     name='kernel_{}'.format(head))
            self.kernels.append(kernel)

            # Layer bias
            if self.use_bias:
                bias = self.add_weight(shape=(self.channels,),
                                       initializer=self.bias_initializer,
                                       regularizer=self.bias_regularizer,
                                       constraint=self.bias_constraint,
                                       name='bias_{}'.format(head))
                self.biases.append(bias)

            # Attention kernels
            attn_kernel_self = self.add_weight(shape=(self.channels, 1),
                                               initializer=self.attn_kernel_initializer,
                                               regularizer=self.attn_kernel_regularizer,
                                               constraint=self.attn_kernel_constraint,
                                               name='attn_kernel_self_{}'.format(head))
            attn_kernel_neighs = self.add_weight(shape=(self.channels, 1),
                                                 initializer=self.attn_kernel_initializer,
                                                 regularizer=self.attn_kernel_regularizer,
                                                 constraint=self.attn_kernel_constraint,
                                                 name='attn_kernel_neigh_{}'.format(head))
            self.attn_kernels.append([attn_kernel_self, attn_kernel_neighs])
        self.built = True

    def call(self, inputs):
        X = inputs[0]  # Node features (N x F)
        A = inputs[1]  # Adjacency matrix (N x N)

        outputs = []
        for head in range(self.attn_heads):
            kernel = self.kernels[head]  # W in the paper (F x F')
            attention_kernel = self.attn_kernels[head]  # Attention kernel a in the paper (2F' x 1)

            # Compute inputs to attention network
            features = K.dot(X, kernel)  # (N x F')

            # Compute feature combinations
            # Note: [[a_1], [a_2]]^T [[Wh_i], [Wh_2]] = [a_1]^T [Wh_i] + [a_2]^T [Wh_j]
            attn_for_self = K.dot(features, attention_kernel[0])    # (N x 1), [a_1]^T [Wh_i]
            attn_for_neighs = K.dot(features, attention_kernel[1])  # (N x 1), [a_2]^T [Wh_j]

            # Attention head a(Wh_i, Wh_j) = a^T [[Wh_i], [Wh_j]]
            if len(K.int_shape(features)) == 2:
                attn_for_neighs_T = K.transpose(attn_for_neighs)
            else:
                attn_for_neighs_T = K.permute_dimensions(attn_for_neighs, (0, 2, 1))
            dense = attn_for_self + attn_for_neighs_T

            # Add nonlinearity
            dense = LeakyReLU(alpha=0.2)(dense)

            # Mask values before activation (Vaswani et al., 2017)
            mask = -10e9 * (1.0 - A)
            dense += mask

            # Apply softmax to get attention coefficients
            dense = K.softmax(dense)  # (N x N)

            # Apply dropout to features and attention coefficients
            dropout_attn = Dropout(self.dropout_rate)(dense)  # (N x N)
            dropout_feat = Dropout(self.dropout_rate)(features)  # (N x F')

            # Linear combination with neighbors' features
            if len(K.int_shape(features)) == 2:
                node_features = K.dot(dropout_attn, dropout_feat)
            else:
                node_features = K.batch_dot(dropout_attn, dropout_feat)

            if self.use_bias:
                node_features = K.bias_add(node_features, self.biases[head])

            # Add output of attention head to final output
            outputs.append(node_features)

        # Aggregate the heads' output according to the reduction method
        if self.attn_heads_reduction == 'concat':
            output = K.concatenate(outputs)  # (N x KF')
        else:
            output = K.mean(K.stack(outputs), axis=0)  # N x F')

        output = self.activation(output)
        return output

    def compute_output_shape(self, input_shape):
        output_shape = input_shape[0][:-1] + (self.output_dim,)
        return output_shape

    def get_config(self):
        config = {
            'channels': self.channels,
            'attn_heads': self.attn_heads,
            'dropout_rate': self.dropout_rate,
            'activation': activations.serialize(self.activation),
            'kernel_initializer': initializers.serialize(self.kernel_initializer),
            'att_kernel_initializer': initializers.serialize(self.attn_kernel_initializer),
            'kernel_regularizer': regularizers.serialize(self.kernel_regularizer),
            'attn_kernel_regularizer': regularizers.serialize(self.attn_kernel_regularizer),
            'activity_regularizer': regularizers.serialize(self.activity_regularizer),
            'kernel_constraint': constraints.serialize(self.kernel_constraint),
            'attn_kernel_constraint': constraints.serialize(self.attn_kernel_constraint),
        }
        base_config = super(GraphAttention, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))


class GraphConvSkip(Layer):
    """
    A graph convolutional layer as presented by
    [Kipf & Welling (2016)](https://arxiv.org/abs/1609.02907), with the addition
    of skip connections.

    **Mode**: single, mixed, batch.

    This layer computes the transformation:
    $$
        Z = \\sigma(A X W_1 + X_0 W_2 + b)
    $$
    where \(X\) is the node features matrix, \(X_0\) is the node features matrix
    for the skip connection, \(A\) is the normalized laplacian,
    \(W_1\) and \(W_2\) are the convolution kernels, \(b\) is a bias vector,
    and \(\\sigma\) is the activation function.

    **Input**

    - node features of shape `(batch, num_nodes, num_features)`, depending on the
    mode;
    - node features for the skip connection of shape
    `(batch, num_nodes, num_features)`, depending on the mode;
    - Laplacians of shape `(batch, num_nodes, num_nodes)`, depending on the mode.
    The Laplacians can be computed from the adjacency matrices using
    `utils.convolution.localpooling_filter`.

    **Output**

    - node features with the same shape of the input, but the last dimension
    changed to `channels`.

    **Arguments**

    - `channels`: integer, number of output channels;
    - `activation`: activation function to use;
    - `use_bias`: whether to add a bias to the linear transformation;
    - `kernel_initializer`: initializer for the kernel matrix;
    - `bias_initializer`: initializer for the bias vector;
    - `kernel_regularizer`: regularization applied to the kernel matrix;
    - `bias_regularizer`: regularization applied to the bias vector;
    - `activity_regularizer`: regularization applied to the output;
    - `kernel_constraint`: constraint applied to the kernel matrix;
    - `bias_constraint`: constraint applied to the bias vector.

    **Usage**
    ```py
    X = Input(shape=(num_nodes, num_features))
    X_0 = Input(shape=(num_nodes, num_features))
    filter = Input((num_nodes, num_nodes))
    Z = GraphConvSkip(units, activation='relu')([X, X_0, filter])
    ```
    """

    def __init__(self,
                 channels,
                 activation=None,
                 use_bias=True,
                 kernel_initializer='glorot_uniform',
                 bias_initializer='zeros',
                 kernel_regularizer=None,
                 bias_regularizer=None,
                 activity_regularizer=None,
                 kernel_constraint=None,
                 bias_constraint=None,
                 **kwargs):
        if 'input_shape' not in kwargs and 'input_dim' in kwargs:
            kwargs['input_shape'] = (kwargs.pop('input_dim'),)
        super(GraphConvSkip, self).__init__(**kwargs)
        self.channels = channels
        self.activation = activations.get(activation)
        self.use_bias = use_bias
        self.kernel_initializer = initializers.get(kernel_initializer)
        self.bias_initializer = initializers.get(bias_initializer)
        self.kernel_regularizer = regularizers.get(kernel_regularizer)
        self.bias_regularizer = regularizers.get(bias_regularizer)
        self.activity_regularizer = regularizers.get(activity_regularizer)
        self.kernel_constraint = constraints.get(kernel_constraint)
        self.bias_constraint = constraints.get(bias_constraint)
        self.supports_masking = False

    def build(self, input_shape):
        assert len(input_shape) >= 2
        input_dim = input_shape[0][-1]
        input_dim_skip = input_shape[1][-1]

        self.kernel_1 = self.add_weight(shape=(input_dim, self.channels),
                                        initializer=self.kernel_initializer,
                                        name='kernel_1',
                                        regularizer=self.kernel_regularizer,
                                        constraint=self.kernel_constraint)
        self.kernel_2 = self.add_weight(shape=(input_dim_skip, self.channels),
                                        initializer=self.kernel_initializer,
                                        name='kernel_2',
                                        regularizer=self.kernel_regularizer,
                                        constraint=self.kernel_constraint)
        if self.use_bias:
            self.bias = self.add_weight(shape=(self.channels,),
                                        initializer=self.bias_initializer,
                                        name='bias',
                                        regularizer=self.bias_regularizer,
                                        constraint=self.bias_constraint)
        else:
            self.bias = None
        self.built = True

    def call(self, inputs):
        features = inputs[0]
        features_skip = inputs[1]
        basis = inputs[2]

        # Convolution
        output = K.dot(features, self.kernel_1)
        if len(K.int_shape(features)) == 2:
            # Single mode
            output = K.dot(basis, output)
        else:
            if len(K.int_shape(basis)) == 3:
                # Batch mode
                output = K.batch_dot(basis, output)
            else:
                # Mixed mode
                output = K.tf.einsum('ij,bjk->bik', basis, output)  # TODO implement in pure Keras

        # Skip connection
        skip = K.dot(features_skip, self.kernel_2)
        output += skip

        if self.use_bias:
            output = K.bias_add(output, self.bias)
        if self.activation is not None:
            output = self.activation(output)
        return output

    def compute_output_shape(self, input_shape):
        features_shape = input_shape[0]
        output_shape = features_shape[:-1] + (self.channels,)
        return output_shape

    def get_config(self):
        config = {
            'units': self.channels,
            'activation': activations.serialize(self.activation),
            'use_bias': self.use_bias,
            'kernel_initializer': initializers.serialize(self.kernel_initializer),
            'bias_initializer': initializers.serialize(self.bias_initializer),
            'kernel_regularizer': regularizers.serialize(self.kernel_regularizer),
            'bias_regularizer': regularizers.serialize(self.bias_regularizer),
            'activity_regularizer': regularizers.serialize(self.activity_regularizer),
            'kernel_constraint': constraints.serialize(self.kernel_constraint),
            'bias_constraint': constraints.serialize(self.bias_constraint)
        }
        base_config = super(GraphConvSkip, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))


class ARMAConv(Layer):
    """
    A graph convolutional layer with ARMA(H, K) filters, as presented by
    [Bianchi et al. (2019)](https://arxiv.org/abs/1901.01343).

    **Mode**: single, mixed, batch.

    This layer computes the transformation:
    $$
        X^{out} = \\dots
    $$
    where ...

    **Input**

    - node features of shape `(batch, num_nodes, num_features)`, depending on the
    mode;
    - normalized Laplacians of shape `(batch, num_nodes, num_nodes)`, depending
    on the mode.

    **Output**

    - node features with the same shape of the input, but the last dimension
    changed to `channels`.

    **Arguments**

    - `channels`: integer, number of output channels;
    - `ARMA_K`: order of the ARMA filter (combination of K ARMA_1 filters);
    - `ARMA_D`: depth of each ARMA_1 filter (number of recursive updates);
    - `recurrent`: whether to share each head's weights like a recurrent net;
    - `activation`: activation function to use;
    - `gcn_activation`: activation function to use to compute the ARMA filter;
    - `dropout_rate`: dropout rate for laplacian and output layer
    - `use_bias`: whether to add a bias to the linear transformation;
    - `kernel_initializer`: initializer for the kernel matrix;
    - `bias_initializer`: initializer for the bias vector;
    - `kernel_regularizer`: regularization applied to the kernel matrix;
    - `bias_regularizer`: regularization applied to the bias vector;
    - `activity_regularizer`: regularization applied to the output;
    - `kernel_constraint`: constraint applied to the kernel matrix;
    - `bias_constraint`: constraint applied to the bias vector.

    **Usage**
    ```py
    fltr = localpooling_filter(adj)
    ...
    X = Input(shape=(num_nodes, num_features))
    filter = Input((num_nodes, num_nodes))
    Z = ARMAConv(units, activation='relu')([X, filter])
    ...
    model.fit([node_features, fltr], y)
    ```
    """

    def __init__(self,
                 channels,
                 ARMA_D,
                 ARMA_K=None,
                 recurrent=False,
                 activation=None,
                 gcn_activation='relu',
                 dropout_rate=0.0,
                 use_bias=True,
                 kernel_initializer='glorot_uniform',
                 bias_initializer='zeros',
                 kernel_regularizer=None,
                 bias_regularizer=None,
                 activity_regularizer=None,
                 kernel_constraint=None,
                 bias_constraint=None,
                 **kwargs):
        if 'input_shape' not in kwargs and 'input_dim' in kwargs:
            kwargs['input_shape'] = (kwargs.pop('input_dim'),)
        super(ARMAConv, self).__init__(**kwargs)
        self.channels = channels
        self.ARMA_D = ARMA_D
        self.ARMA_K = ARMA_D if ARMA_K is None else ARMA_K
        self.recurrent = recurrent
        self.activation = activations.get(activation)
        self.gcn_activation = activations.get(gcn_activation)
        self.dropout_rate = dropout_rate
        self.use_bias = use_bias
        self.kernel_initializer = initializers.get(kernel_initializer)
        self.bias_initializer = initializers.get(bias_initializer)
        self.kernel_regularizer = regularizers.get(kernel_regularizer)
        self.bias_regularizer = regularizers.get(bias_regularizer)
        self.activity_regularizer = regularizers.get(activity_regularizer)
        self.kernel_constraint = constraints.get(kernel_constraint)
        self.bias_constraint = constraints.get(bias_constraint)
        self.supports_masking = False

    def build(self, input_shape):
        assert len(input_shape) >= 2
        # When using shared weights, pre-compute them here
        if self.recurrent:
            self.kernels_in = []  # Weights from input space to output space
            self.kernels_hid = []  # Weights from output space to output space
            for k in range(self.ARMA_K):
                self.kernels_in.append(self.get_gcn_weights(input_shape[0][-1],
                                                            input_shape[0][-1],
                                                            self.channels,
                                                            name='ARMA_skip_{}r_in'.format(k),
                                                            use_bias=self.use_bias,
                                                            kernel_initializer=self.kernel_initializer,
                                                            bias_initializer=self.bias_initializer,
                                                            kernel_regularizer=self.kernel_regularizer,
                                                            bias_regularizer=self.bias_regularizer,
                                                            kernel_constraint=self.kernel_constraint,
                                                            bias_constraint=self.bias_constraint))
                if self.ARMA_D > 1:
                    self.kernels_hid.append(self.get_gcn_weights(self.channels,
                                                                 input_shape[0][-1],
                                                                 self.channels,
                                                                 name='ARMA_skip_{}r_hid'.format(k),
                                                                 use_bias=self.use_bias,
                                                                 kernel_initializer=self.kernel_initializer,
                                                                 bias_initializer=self.bias_initializer,
                                                                 kernel_regularizer=self.kernel_regularizer,
                                                                 bias_regularizer=self.bias_regularizer,
                                                                 kernel_constraint=self.kernel_constraint,
                                                                 bias_constraint=self.bias_constraint))
        self.built = True

    def call(self, inputs):
        features = inputs[0]
        basis = inputs[1]

        # Convolution
        output = []  # Stores the parallel filters
        for k in range(self.ARMA_K):
            output_k = features
#            basis_drop = Dropout(self.dropout_rate)(basis)
            basis_drop = basis
            for d in range(self.ARMA_D):
                features_drop = Dropout(self.dropout_rate)(features)
                output_k = self.graph_conv_skip([output_k, features_drop, basis_drop],
                                                self.channels,
                                                'ARMA_skip_{}{}'.format(k, d),
                                                recurrent_k=k if self.recurrent else None,
                                                recurrent_d=d if self.recurrent else None,
                                                activation=self.gcn_activation,
                                                use_bias=self.use_bias,
                                                kernel_initializer=self.kernel_initializer,
                                                bias_initializer=self.bias_initializer,
                                                kernel_regularizer=self.kernel_regularizer,
                                                bias_regularizer=self.bias_regularizer,
                                                kernel_constraint=self.kernel_constraint,
                                                bias_constraint=self.bias_constraint)
            output.append(output_k)

        # Aggregate parallel filters
        output = K.concatenate(output, axis=-1)
                
        # Avrage pooling
        output = K.expand_dims(output, axis=-1)
        output_dim = K.int_shape(output)
        if len(output_dim) == 3: # [nodes, feat, 1] -> [nodes, feat_red, 1]
            output = AveragePooling1D(pool_size=self.ARMA_K, padding='same')(output)
        elif len(output_dim) == 4: # [batch, nodes, feat, 1] -> [batch, nodes, feat_red, 1]
            output = AveragePooling2D(pool_size=(1, self.ARMA_K), padding='same')(output)
        else:
            raise RuntimeError('GCN_ARMA layer: wrong output dim')
        output = K.squeeze(output, axis=-1)
        
        output = self.activation(output)
        
        return output

    def compute_output_shape(self, input_shape):
        features_shape = input_shape[0]
        output_shape = features_shape[:-1] + (self.channels,)
        return output_shape

    def get_config(self):
        config = {
            'units': self.channels,
            'activation': activations.serialize(self.activation),
            'use_bias': self.use_bias,
            'kernel_initializer': initializers.serialize(self.kernel_initializer),
            'bias_initializer': initializers.serialize(self.bias_initializer),
            'kernel_regularizer': regularizers.serialize(self.kernel_regularizer),
            'bias_regularizer': regularizers.serialize(self.bias_regularizer),
            'activity_regularizer': regularizers.serialize(self.activity_regularizer),
            'kernel_constraint': constraints.serialize(self.kernel_constraint),
            'bias_constraint': constraints.serialize(self.bias_constraint)
        }
        base_config = super(ARMAConv, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))

    def get_gcn_weights(self, input_dim, input_dim_skip, channels, name,
                        use_bias=True,
                        kernel_initializer='glorot_uniform',
                        bias_initializer='zeros',
                        kernel_regularizer=None,
                        bias_regularizer=None,
                        kernel_constraint=None,
                        bias_constraint=None):
        """
        Creates a set of weights for a GCN with skip connections
        :param input_dim: dimension of the input space of the layer
        :param input_dim_skip: dimension of the input space for the skip connection
        :param channels: dimension of the output space
        :param name: name of the layer
        :param use_bias: whether to create a bias vector (if False, returns None as bias)
        :param kernel_initializer: initializer for the kernels
        :param bias_initializer: initializer for the bias
        :param kernel_regularizer: regularizer for the kernels
        :param bias_regularizer: regularizer for the bias
        :param kernel_constraint: constraint for the kernel
        :param bias_constraint: constraint for the bias
        :return:
            - kernel_1, from input space of the layer to output space
            - kernel_2, from input space of the skip connection to output space
            - bias, bias vector on the output space if use_bias=True, None otherwise.
        """
        kernel_initializer = initializers.get(kernel_initializer)
        kernel_regularizer = regularizers.get(kernel_regularizer)
        kernel_constraint = constraints.get(kernel_constraint)
        bias_initializer = initializers.get(bias_initializer)
        bias_regularizer = regularizers.get(bias_regularizer)
        bias_constraint = constraints.get(bias_constraint)
        kernel_1 = self.add_weight(shape=(input_dim, channels),
                                   name=name + '_kernel_1',
                                   initializer=kernel_initializer,
                                   regularizer=kernel_regularizer,
                                   constraint=kernel_constraint)
        kernel_2 = self.add_weight(shape=(input_dim_skip, channels),
                                   name=name + '_kernel_2',
                                   initializer=kernel_initializer,
                                   regularizer=kernel_regularizer,
                                   constraint=kernel_constraint)
        if use_bias:
            bias = self.add_weight(shape=(channels,),
                                   name=name + '_bias',
                                   initializer=bias_initializer,
                                   regularizer=bias_regularizer,
                                   constraint=bias_constraint)
        else:
            bias = None
        return kernel_1, kernel_2, bias

    def graph_conv_skip(self, x, channels, name,
                        recurrent_k=None,
                        recurrent_d=None,
                        activation=None,
                        use_bias=True,
                        kernel_initializer='glorot_uniform',
                        bias_initializer='zeros',
                        kernel_regularizer=None,
                        bias_regularizer=None,
                        kernel_constraint=None,
                        bias_constraint=None):
        """
        Creates a graph convolutional layer with a skip connection
        :param x: list of input tensors, namely
            - input of the layer
            - input for the skip connection
            - laplacian, or normalized adjacency matrix
        :param channels: dimension of the output space
        :param name: name of the layer
        :param recurrent_k: if the recurrent flag was set, then use the shared
        weights of the k-th filter when creating the layer
        :param recurrent_d: if the recurrent flag was set, then use the shared
        weights when computing the i-th recursive step of the k-th filter.
        Note that this parameter cannot be None if reccurent_k is not None.
        :param activation: activation function for the layer
        :param use_bias: whether to add a bias vector
        :param kernel_initializer: initializer for the kernels
        :param bias_initializer: initializer for the bias
        :param kernel_regularizer: regularizer for the kernels
        :param bias_regularizer: regularizer for the bias
        :param kernel_constraint: constraint for the kernel
        :param bias_constraint: constraint for the bias
        :return: output of the layer
        """
        input_dim = K.int_shape(x[0])[-1]
        input_dim_skip = K.int_shape(x[1])[-1]

        if recurrent_k is None:
            kernel_1, kernel_2, bias = self.get_gcn_weights(input_dim,
                                                            input_dim_skip,
                                                            channels,
                                                            name,
                                                            kernel_initializer=kernel_initializer,
                                                            bias_initializer=bias_initializer,
                                                            kernel_regularizer=kernel_regularizer,
                                                            bias_regularizer=bias_regularizer,
                                                            kernel_constraint=kernel_constraint,
                                                            bias_constraint=bias_constraint)
        else:
            # When using shared weights, use the pre-computed ones.
            if recurrent_d is None:
                raise ValueError('recurrent_k and recurrent_d must be set together.')
            if recurrent_d == 0:
                kernel_1, kernel_2, bias = self.kernels_in[recurrent_k]
            else:
                kernel_1, kernel_2, bias = self.kernels_hid[recurrent_k]
        features = x[0]
        features_skip = x[1]
        basis = x[2]

        # Convolution
        output = K.dot(features, kernel_1)
        if len(K.int_shape(features)) == 2:
            # Single mode
            output = K.dot(basis, output)
        else:
            if len(K.int_shape(basis)) == 3:
                # Batch mode
                output = K.batch_dot(basis, output)
            else:
                # Mixed mode
                output = K.tf.einsum('ij,bjk->bik', basis, output)  # TODO implement in pure Keras

        # Skip connection
        skip = K.dot(features_skip, kernel_2)
        output += skip

        if use_bias:
            output = K.bias_add(output, bias)
        if activation is not None:
            output = activations.get(activation)(output)
        return output
