import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import backend
import os
import numpy as np

class ConvNet:
    '''
        Convolutional Autoencoder Network
    '''
    def __init__(self):

        self.callbacks = []

    def reinitialise(self):
        self.callbacks = []
        backend.clear_session()
        tf.reset_default_graph()

    def tensorboard(self,log='tensorboard/covnet_autoencoder'):
        '''
            Tensorboard
        '''
        self.callbacks.append(keras.callbacks.TensorBoard(log_dir=log,write_graph=True, write_images=True))


    def checkpoints(self,path='training',N=10):
        checkpoint_path = os.path.join(path,"cp-{epoch:04d}.ckpt")

        # Create checkpoint callback
        self.callbacks.append(tf.keras.callbacks.ModelCheckpoint(checkpoint_path,
                                                         save_weights_only=True,
                                                         verbose=1, period=N))

    def model(self,height,width,channels=1):
        '''
            Build the model
            The encoder will consist in a stack of Conv2D and MaxPooling2D layers
            (max pooling being used for spatial down-sampling), while the decoder will
            consist in a stack of Conv2D and UpSampling2D layers.
        '''
        input_img = keras.layers.Input(shape=(height, width, channels))

        x = keras.layers.Conv2D(16, (3, 3), activation='relu', padding='same')(input_img)
        x = keras.layers.MaxPooling2D((2, 2), padding='same')(x)
        x = keras.layers.Conv2D(8, (3, 3), activation='relu', padding='same')(x)
        x = keras.layers.MaxPooling2D((2, 2), padding='same')(x)
        x = keras.layers.Conv2D(8, (3, 3), activation='relu', padding='same')(x)
        encoded = keras.layers.MaxPooling2D((2, 2), padding='same')(x)

        x = keras.layers.Conv2D(8, (3, 3), activation='relu', padding='same')(encoded)
        x = keras.layers.UpSampling2D((2, 2))(x)
        x = keras.layers.Conv2D(8, (3, 3), activation='relu', padding='same')(x)
        x = keras.layers.UpSampling2D((2, 2))(x)
        x = keras.layers.Conv2D(16, (3, 3), activation='relu')(x)
        x = keras.layers.UpSampling2D((2, 2))(x)
        decoded = keras.layers.Conv2D(1, (3, 3), activation='sigmoid', padding='same')(x)

        self.autoencoder = keras.models.Model(input_img, decoded)
        # self.autoencoder.compile(optimizer='adadelta', loss='binary_crossentropy' )
        self.autoencoder.compile(optimizer='Adam', loss='mean_squared_error' )

    def model_summary(self):
        '''
        	Model Summary
        '''
        self.autoencoder.summary()

    def train(self,X,epoch=100,batch_size=256):
        '''
            Train the model
            X samples should be in the range [0,1]
        '''

        self.autoencoder.fit(X, X,
                        epochs=epoch,
                        batch_size=batch_size,
                        shuffle=True,
                        # validation_data=(test_images, test_images),
                        callbacks=self.callbacks)


    def save_model(self, path='model.h5'):
        self.autoencoder.save_weights(path)

    def load_model(self,path='model.h5'):
        self.autoencoder.load_weights(path)


    def maxsse(self, height, width):
        '''
            calculate the maximum sse posible given the width and height of samples
        '''
        x = np.array(np.zeros((height,width)))
        y = np.array(np.ones((height,width)))
        return np.sum(np.power(np.subtract(x,y),2))

    def sse(self, x):
        '''
            return sum of squared error between input x and output x'
        '''
        decoded = self.autoencoder.predict(x[np.newaxis,:,:,:])
        return np.sum(np.power(np.subtract(x,decoded),2))

    def decode(self, X):
        '''
            return sum of squared error between input x and output x'
            X [samples, height,width, 1]
        '''
        return self.autoencoder.predict(X)