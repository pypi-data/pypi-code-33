"""
Class for dealing with word embeddings
"""

import numpy as np

from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences

def load_from_text(path):
    """
    A functions that loads embeddings from a txt document
    """
    def get_coefs(word,*arr): return word, np.asarray(arr, dtype='float32')
    emb = dict(get_coefs(*o.split(" ")) for o in open(path, 
                                                      encoding = 'utf-8',
                                                      errors='ignore'))
    return emb

def tokenize_text(string_list, max_features, max_len):
    """
    Tokenizes a given string list
    max_featues - number of unique tokens to use in final matrix
    max_len - number of unique tokens to use in each list element
    """
    tokenizer = Tokenizer(num_words = max_features)
    tokenizer.fit_on_texts(string_list)
    token = tokenizer.texts_to_sequences(string_list)
    token = pad_sequences(token, maxlen = max_len)
    
    return token, tokenizer

def create_embedding_matrix(embeddings, tokenizer, max_features, 
                            embed_size = 300): 
    """
    Function to create the embedding matrix to use in neural networks
    embeddings - output of load_from_text() function
    tokenizer - output of tokenize_text() function
    max_features - constant; how many unique tokens to use
    embed_size - constant; how many coordinates does the read embedding has
    """
    embedding_matrix = np.zeros((max_features, embed_size))
    for word, index in tokenizer.word_index.items():
        if index > max_features - 1:
            break
        else:
            try:
                embedding_matrix[index] = embeddings[word]
            except:
                continue
    return embedding_matrix        
    