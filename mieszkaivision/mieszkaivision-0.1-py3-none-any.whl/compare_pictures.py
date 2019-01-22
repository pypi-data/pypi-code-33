# Packages for training algorithms and visualize
import numpy as np
from app.picture_classifier_umap import NeuralTransformer
import pickle
import matplotlib as mpl
mpl.use('TkAgg')

def compare_pictures(path_in, embedding, train_list, embedding_train):
    """
    :param path_in:
    List of url addresses with flat's images
    :param embedding:
    model with trained embedding, loaded from pickle file inside app
    :param train_list:
    list with images of apartments
    :param embedding_train:
    results of embedding on training set, the same as in train_list
    :return:
    Most similar picture based on Euclidean distance between embeddings
    """
    # Transform to two dimensional representation

    classifier = NeuralTransformer(path_in)
    test_features = classifier.fit_neural()
    embedding_test = embedding.transform(test_features)

    # Calculate Euclidean distance between points obtained from umap
    distance = []
    for single_embedding_test in embedding_test:
        distance.append(np.sum((embedding_train - single_embedding_test) ** 2, axis=1))

    # Find element that's closest in training set
    closest_element = []
    for dist in distance:
        closest_element.append(train_list[np.argmin(dist)])

    return closest_element


def get_url_origin(addresses, closest_elements):
    """
    :param addresses:
    Source data frame with addresses of urls
    The assumption is that data frame contains columns named 'addresses'
    :param closest_elements:
    List contaning urls for apartments photographs
    :return:
    Origin of urls for apartments
    """
    origin_urls = []
    for closest_element in closest_elements:
        origin_urls.append(addresses[addresses['addresses'].apply(lambda x: closest_element in x)]['url'].tolist()[0])

    return origin_urls
