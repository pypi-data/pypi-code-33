import os
import zipfile
import shutil
import numpy as np
from sklearn.preprocessing import LabelEncoder, OneHotEncoder


def to_categorical(y, num_classes=None):
    """
    Converts a class vector (integers) to binary class matrix.
    E.g. for use with categorical_crossentropy.
    Arguments:
          y: class vector to be converted into a matrix
          (integers from 0 to num_classes).
        num_classes: total number of classes.
    Returns:
          A binary matrix representation of the input. The classes axis is placed
        last.
    """
    y = np.array(y, dtype='int')
    input_shape = y.shape
    if input_shape and input_shape[-1] == 1 and len(input_shape) > 1:
        input_shape = tuple(input_shape[:-1])
    y = y.ravel()
    if not num_classes:
        num_classes = np.max(y) + 1
    n = y.shape[0]
    categorical = np.zeros((n, num_classes), dtype=np.float32)
    categorical[np.arange(n), y] = 1
    output_shape = input_shape + (num_classes,)
    categorical = np.reshape(categorical, output_shape)
    return categorical

def normalize(x, axis=-1, order=2):
    """
    Normalizes a Numpy array.
    Arguments:
        x: Numpy array to normalize.
        axis: axis along which to normalize.
        order: Normalization order (e.g. 2 for L2 norm).
    Returns:
        A normalized copy of the array.
    """
    l2 = np.atleast_1d(np.linalg.norm(x, order, axis))
    l2[l2 == 0] = 1
    return x / np.expand_dims(l2, axis)


def get_extension(fname):
    filename, file_extension = os.path.splitext(fname)
    return file_extension

def extract(path,fname):
    ext = get_extension(fname)
    f = os.path.join(path,fname)
    print("Extracting data from ",p)
    
    if ext=='.zip':
        k = zipfile.ZipFile(f,"r")
        k.extractall(path)
    print("Extraction Sucessfull")
        
def prepare_labels(y):
    values = np.array(y)
    label_encoder = LabelEncoder()
    integer_encoded = label_encoder.fit_transform(values)

    onehot_encoder = OneHotEncoder(sparse=False)
    integer_encoded = integer_encoded.reshape(len(integer_encoded), 1)
    onehot_encoded = onehot_encoder.fit_transform(integer_encoded)

    y = onehot_encoded
    return y, label_encoder