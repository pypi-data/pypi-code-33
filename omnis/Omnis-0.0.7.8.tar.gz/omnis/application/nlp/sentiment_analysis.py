from keras import models
from keras.layers import Input, Dense
from keras.layers import Embedding, Dropout
from keras.layers import Conv1D
from keras.layers import GlobalMaxPooling1D
from keras.layers import Activation

from keras import layers

from ..application import Application

from ...lib.general_lib import *

from ...lib.text_lib import get_words_from_text

import numpy as np

import random

from keras.preprocessing import sequence

import keras



class Sentiment_Analysis(Application):
    def __init__(self, model_path = None):
        """Initializes a model.
        
        Arguments:
            Application {class} -- A super class of neural network models.
        
        Keyword Arguments:
            model_path {str} -- A path of model file. (default: {None})
        """        
        if type(model_path) != type(None):
            Application.__init__(self, model_path)
        else:
            Application.__init__(self)

    def set_input_dictionary(self, input_dictionary):
        self.model.input_dictionary = input_dictionary
        self.model.__class__.input_dictionary = self.model.input_dictionary

    def init_input_data(self, sentiment_texts):
        """Initializes input data for training or prediction.
        
        Arguments:
            sentiment_texts {list} -- An input list of texts.
        
        Returns:
            [ndarray] -- 2D-ndarray of int32.(encoded by input_dictionary)
        """
        x = []
        for i, text in enumerate(sentiment_texts):
            word_list = get_words_from_text(text.lower()) # we will lower all words
            single_element = list()
            for word in word_list:                
                if word in self.model.input_dictionary:
                    single_element.append( self.model.input_dictionary[word] )
            x.append(single_element)
        x = sequence.pad_sequences(x, maxlen = self.input_shape[0])
        return x
    
    def prepare_train_data(self, sentiment_texts, sentiment_values, skip_top, num_of_words_to_consider, max_num_of_word = 150):
        """Prepares training data.
        
        Arguments:
            sentiment_texts {list} -- A list of sentiment texts.
            sentiment_values {list} -- A list of sentiment values.
            skip_top {int} -- Top most frequent words to ignore. Like and, are, is, I, etc.
            num_of_words_to_consider {int} -- Top most frequent words to consider except skip_top.
        
        Keyword Arguments:
            max_num_of_word {int} -- A max number of words in each text of sentiment_texts (default: {150})
        """
        if hasattr(self, 'input_shape') == False:
            word_freq_dict = dict()
            for text in sentiment_texts:
                word_list = get_words_from_text(text.lower()) # we will lower all words
                for word in word_list:
                    if word in word_freq_dict:
                        word_freq_dict[word] += 1
                    else:
                        word_freq_dict[word] = 1
            sorted_words = sorted(word_freq_dict.items(), key = lambda x:x[1], reverse = True)
            words_to_consider = sorted_words[skip_top : skip_top + num_of_words_to_consider]
            input_dictionary = dict()
            for i, word_tuple in enumerate(words_to_consider):
                input_dictionary[word_tuple[0]] = i
            self.input_shape = ( max_num_of_word, )
            num_classes = len(set(sentiment_values))
            self.model = self.create_model( len(input_dictionary), num_classes )
            self.set_input_dictionary(input_dictionary)
        self.x = self.init_input_data(sentiment_texts)
        self.y = keras.utils.to_categorical(np.asarray(sentiment_values), num_classes = self.model.output_shape[1])

    def create_model(self, input_dim, num_classes):
        input_layer = Input(shape = self.input_shape)
        embedding1 = Embedding(input_dim, 128, input_length = self.input_shape[0])(input_layer)
        drop1 = Dropout(0.2)(embedding1)
        conv1 = Conv1D(64, 5, padding='valid', activation='relu', strides=1)(drop1)
        pool1 = GlobalMaxPooling1D()(conv1)
        dense1 = Dense(256)(pool1)
        drop2 = Dropout(0.2)(dense1)
        act1 = Activation('relu')(drop2)
        output_layer = Dense(num_classes, activation = 'sigmoid')(act1)
        return models.Model(inputs=input_layer, outputs=output_layer)

    def train(self,
            optimizer = 'nadam',
            metrics = ['accuracy'],
            batch_size = None,
            steps_per_epoch = None,
            epochs = 1,
            verbose = 1,
            callbacks = None,
            shuffle = True):
            self.compile_model(optimizer = optimizer, loss = 'categorical_crossentropy', metrics = metrics)
            self.model.fit(self.x, self.y, batch_size=batch_size, steps_per_epoch=steps_per_epoch, epochs = epochs, verbose = verbose, callbacks = callbacks, shuffle = shuffle)
