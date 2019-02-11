from keras.models import Model
from keras.layers import Input, Embedding, Add, Lambda, RepeatVector, Permute, Activation
import keras.backend as K

from transformer_keras.layers import PosLayer, MaskLayer, transformer_block



def base_model(max_length: int,
               voc_size: int,
               num_layers:int,
               model_dim: int,
               n_head,
               dropout_rate: float,
               d_inner_hid: int):
    input_layer = Input(batch_shape=(None,max_length))
    pos = PosLayer(max_length)(input_layer)

    word_embedding = Embedding(input_dim=voc_size,
                               output_dim=model_dim,
                               name='WordEmbedding')(input_layer)
    pos_embedding = Embedding(input_dim=max_length,
                              output_dim=model_dim)(pos)
    x = Add()([word_embedding,pos_embedding])
    mask = MaskLayer()(input_layer)


    for i in range(num_layers):
        x = transformer_block(x,mask,n_head,model_dim,dropout_rate,d_inner_hid)
    model = Model(input_layer,x)
    return model

def get_pretrain_model(base_model: Model,max_length: int, model_dim:int):
    p_mask_input = Input(batch_shape=(None,max_length),dtype='float32')
    p_mask = RepeatVector(model_dim)(p_mask_input)
    p_mask = Permute((2, 1))(p_mask)


    decoder = Lambda(lambda x:x[0]*x[1])([base_model.output,p_mask])
    decoder = Lambda(lambda x:K.sum(x,1))(decoder)
    decoder = Lambda(lambda x: K.dot(x, K.transpose(base_model.get_layer('WordEmbedding').weights[0])),
                     name='lm_logits')(decoder)
    decoder = Activation('softmax')(decoder)
    model = Model(inputs=[base_model.input,p_mask_input],outputs=[decoder])
    model.compile(optimizer='adam',loss='sparse_categorical_crossentropy')
    return base_model,model





if __name__=='__main__':
    import numpy as np
    b = base_model(200,500,3,128,8,0.1,256)
    print(b.summary())
    b,model = get_pretrain_model(b,200,128)
    X = np.array([[1,1,1,1]+196*[0]]*100)
    X_mask = np.array([[0,1,0,0]+196*[0]]*100)
    Y_mask = np.array([1]*100)
    print(b.get_weights())
    model.fit([X,X_mask],Y_mask)
    print(b.get_weights())

    # t = model.predict(np.array([[1,1,1,1]+196*[0]]))
    # print(t,t.shape)
    # from keras.losses import sparse_categorical_crossentropy
    # model.fit

