# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Utilities to train a surrogate model from teacher."""

import numpy as np


def soft_logit(values, clip_val=5):
    """Compute a soft logit on an iterable by bounding outputs to a min/max value.

    :param values: Iterable of numeric values to logit and clip.
    :type values: iter
    :param clip_val: Clipping threshold for logit output.
    :type clip_val: Union[Int, Float]
    """
    new_values = np.log(values / (1 - values))
    return np.clip(new_values, -clip_val, clip_val)


def model_distill(teacher_model_predict_fn, uninitialized_surrogate_model, data):
    """Teach a surrogate model to mimic a teacher model.

    :param teacher_model_predict_fn: Blackbox model's prediction function.
    :type teacher_model_predict_fn: function
    :param uninitialized_surrogate_model: Uninitialized model used to distill blackbox.
    :type uninitialized_surrogate_model: uninitialized model
    :param data: Representative data (or training data) to train distilled model.
    :type data: numpy.ndarray
    """
    # For regression, teacher_y is a real value whereas for classification it is a probability between 0 and 1
    teacher_y = teacher_model_predict_fn(data)
    multiclass = False
    is_classifier = len(teacher_y.shape) == 2
    # If the predict_proba function returned one column but this is a classifier, modify to [1-p, p]
    if is_classifier and teacher_y.shape[1] == 1:
        teacher_y = np.column_stack((1 - teacher_y, teacher_y))
    if is_classifier and teacher_y.shape[1] > 2:
        # If more than two classes, use multiclass surrogate
        multiclass = True
        surrogate_model = uninitialized_surrogate_model(multiclass=multiclass)
    else:
        surrogate_model = uninitialized_surrogate_model()
    if is_classifier and teacher_y.shape[1] == 2:
        # Make sure output has only 1 dimension
        teacher_y = teacher_y[:, 1]
        # Transform to logit space and fit regression
        surrogate_model.fit(data, soft_logit(teacher_y))
    else:
        # Use hard labels for regression or multiclass case
        training_labels = teacher_y
        if multiclass:
            # For multiclass case, we need to train on the class label
            training_labels = np.argmax(teacher_y, axis=1)
        surrogate_model.fit(data, training_labels)
    return surrogate_model
