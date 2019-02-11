from keras.engine import Layer
from keras import backend as K
import keras
import numpy as np
import tensorflow as tf
from keras import layers
from keras.initializers import Ones, Zeros

neg_inf = -1e19


def scale_dot_product(query: tf.Tensor,
                      key: tf.Tensor,
                      value: tf.Tensor,
                      attn_mask=None):
    '''
    implement of scaled dot-product attention
    :param query: batch_size * seq_length * hidden
    :param key:
    :param value:
    :param attn_mask: batch_size * seq_length, if position i is masked then attn_mask[i] = 0, else attn_mask[i] = 1
    :return:
    '''
    # assert query.shape==key.shape,'query:{},key:{}'.format(query.shape,key.shape)
    shape_list = list(value.shape)
    mul = K.batch_dot(query,K.permute_dimensions(key,(0,2,1)))
    if attn_mask is not None:
        mul = attn_mask * mul + (1.0 - attn_mask) * neg_inf
    scale = mul / K.sqrt(K.cast(shape_list[-1], mul.dtype))
    softmax = K.softmax(scale)
    result = K.batch_dot(softmax,value)
    return result


class SelfAttention(Layer):
    def call(self,x):
        '''
        :param x: if use mask, [attn,mask_attn], else attn
        :return:
        '''
        if isinstance(x,list):
            attn,attn_mask = x
            return scale_dot_product(attn,attn,attn,attn_mask)
        else:
            attn = x
            return scale_dot_product(attn, attn, attn, None)
    def compute_output_shape(self, input_shape):
        return input_shape

class MultiHeadAttention(Layer):
    def __init__(self,n_head: int, model_dim: int, **kwargs):
        self.n_head = n_head
        self.model_dim = model_dim
        self.dim_per_head = model_dim // n_head
        super(MultiHeadAttention,self).__init__(**kwargs)
    def build(self, input_shape):
        if isinstance(input_shape,list):
            input_shape = input_shape[0]

        self.query_kernel = self.add_weight(name='query_kernel',
                                            shape=(input_shape[2],self.dim_per_head*self.n_head),
                                            initializer='uniform',
                                            trainable=True)

        self.key_kernel = self.add_weight(name='key_kernel',
                                            shape=(input_shape[2],self.dim_per_head*self.n_head),
                                            initializer='uniform',
                                            trainable=True)


        self.value_kernel = self.add_weight(name='value_kernel',
                                            shape=(input_shape[2],self.dim_per_head*self.n_head),
                                            initializer='uniform',
                                            trainable=True)

        self.output_kernel = self.add_weight(name='output_kernel',
                                             shape=(self.dim_per_head*self.n_head,self.model_dim),
                                             initializer='uniform',
                                             trainable=True)

        self.output_bias = self.add_weight(name='output_bias',
                                           shape=(self.model_dim,),
                                           initializer='zeros',
                                           trainable=True)

        super(MultiHeadAttention,self).build(input_shape)
    def call(self,x):
        if isinstance(x,list):
            attn,attn_mask = x
            attn_mask = K.repeat_elements(attn_mask, self.n_head,0)
        else:
            attn = x
            attn_mask = None
        query_big = K.dot(attn, self.query_kernel)
        key_big = K.dot(attn, self.key_kernel)
        value_big = K.dot(attn, self.value_kernel) # batch ,seq_len, hid*n_head

        def reshape1(x):
            s = list(x.shape)
            x = K.reshape(x, [-1,s[1],self.n_head,s[2]//self.n_head])
            x = K.permute_dimensions(x, [2,0,1,3])
            x = K.reshape(x, [-1,s[1],s[2]//self.n_head])
            return x

        query_big = reshape1(query_big)
        key_big = reshape1(key_big)
        value_big = reshape1(value_big)

        # print(value_big.shape)

        result = scale_dot_product(query_big,key_big,value_big,attn_mask) # n_head * batch, seq_len, hid

        def reshape2(x):
            s = list(x.shape)  # [n_head * batch_size, len_v, d_v]
            x = K.reshape(x, [self.n_head, -1, s[1], s[2]])
            x = K.permute_dimensions(x, [1, 2, 0, 3])
            x = K.reshape(x, [-1, s[1], self.n_head * s[2]])  # [batch_size, len_v, n_head * d_v]
            return x

        result = reshape2(result)
        result = K.dot(result,self.output_kernel) + self.output_bias
        return result

    def compute_output_shape(self, input_shape):
        if isinstance(input_shape,list):
            input_shape = input_shape[0]
        return (input_shape[0],input_shape[1],self.model_dim)

class MaskLayer(Layer):
    def call(self, inputs, **kwargs):
        mask = K.not_equal(inputs,K.zeros_like(inputs))
        mask = K.cast(mask,inputs.dtype)
        mask = K.reshape(mask,[-1,int(inputs.shape[1]),1])
        return mask
    def compute_output_shape(self, input_shape):
        return (input_shape[0],input_shape[1],1)

class PosLayer(Layer):
    def __init__(self,max_length,**kwargs):
        self.max_length = max_length
        super(PosLayer,self).__init__(**kwargs)
    def call(self, inputs, **kwargs):
        pos = K.arange(0,self.max_length)

        result = K.ones_like(inputs,'int32') * pos
        return result
    def compute_output_shape(self, input_shape):
        return input_shape



class LayerNormalization(Layer):
    def __init__(self, eps=1e-6, **kwargs):
        self.eps = eps
        super(LayerNormalization, self).__init__(**kwargs)

    def build(self, input_shape):
        self.gamma = self.add_weight(name='gamma', shape=input_shape[-1:],
                                     initializer=Ones(), trainable=True)
        self.beta = self.add_weight(name='beta', shape=input_shape[-1:],
                                    initializer=Zeros(), trainable=True)
        super(LayerNormalization, self).build(input_shape)

    def call(self, x):
        mean = K.mean(x, axis=-1, keepdims=True)
        std = K.std(x, axis=-1, keepdims=True)
        return self.gamma * (x - mean) / (std + self.eps) + self.beta

    def compute_output_shape(self, input_shape):
        return input_shape


def transformer_block(x,x_mask,n_head,model_dim, dropout_rate, d_inner_hid):
    '''

    :param x: input tensor (batch size,seq length,dim)
    :param x_mask: mask (batch size, seq length, 1), 0 if masked else 1
    :param n_head:
    :param model_dim:
    :param dropout_rate:
    :param d_inner_hid:
    :return:
    '''
    res = x
    if x_mask is not None:
        x = MultiHeadAttention(n_head,model_dim)([x,x_mask])
    else:
        x = MultiHeadAttention(n_head,model_dim)(x)
    x = layers.Dropout(dropout_rate)(x)
    x = layers.Add()([x,res])
    x = LayerNormalization()(x)

    res = x
    x = layers.Conv1D(d_inner_hid,1,activation='relu')(x)
    x = layers.Conv1D(model_dim,1)(x)
    x = layers.Dropout(dropout_rate)(x)
    x = layers.Add()([x,res])
    x = LayerNormalization()(x)

    return x




if __name__=='__main__':
    # Q = tf.constant(np.array([[[0.0,1.0],[1.0,2.0]]]))
    # m = tf.constant(np.array([[1.0,0.0]]))
    # print(scale_dot_product(Q,Q,Q,m))
    #
    # inp = layers.Input(batch_shape=(None,512,32))
    # inp_m = layers.Input(batch_shape=(None,512))
    # x = MultiHeadAttention(3,5)([inp,inp_m])
    inp = layers.Input(batch_shape=(None,512))
    pos_emb = PosLayer(512)(inp)
    mask_1 = MaskLayer()(inp)
    emb = layers.Embedding(500,768)(inp)
    x = transformer_block(emb,mask_1,8,768,0.1,2048)
    model = keras.Model(inp,[x,mask_1,pos_emb])
    print(model.summary())
    X = np.array([[1,2,3,4,5]+[0]*507])
    print(model.predict(X))






