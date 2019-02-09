import numpy as np
from art.classifiers import KerasClassifier


def get_confusion_matrix(classifier, x_set, y_set, target_label):
    """
    Gets the confusion matrix for a given classifier, data set, and target label

    :param classifier: ART Keras classifier
    :param x_set: test data set
    :param y_set: test data set actual labels
    :param target_label: target label for confusion matrix calculation
    :returns: quadruple containing confusion matrix in the form (% TP, % FP, % FN, % TN)
    """

    # These hold the amount of each type of prediction
    num_true_positive = 0
    num_true_negative = 0
    num_false_positive = 0
    num_false_negative = 0

    # Run test data set through classifier
    preds = np.argmax(classifier.predict(x_set), axis=1)

    # Determine the amount of each type of prediction
    for i in range(x_set.shape[0]):
        if target_label == np.where(y_set[i] == 1.0)[0][0]:
            if preds[i] == np.where(y_set[i] == 1.0)[0][0]:
                num_true_positive += 1
            else:
                num_false_negative += 1
        else:
            if preds[i] != target_label:
                num_true_negative += 1
            else:
                num_false_positive += 1

    # We're interested in the percentage that each type of prediction makes up of all predictions
    percent_true_positive = num_true_positive / preds.shape[0]
    percent_false_positive = num_false_positive / preds.shape[0]
    percent_false_negative = num_false_negative / preds.shape[0]
    percent_true_negative = num_true_negative / preds.shape[0]

    return percent_true_positive, percent_false_positive, percent_false_negative, percent_true_negative


def get_confusion_matrix_difference(classifier, x_set, y_set, target_label, epsilon, adversarial_attack):
    """
    Gets the differences in classification categories of an un-tampered data set and an adversarial data set.

    :param classifier: ART Keras classifier
    :param x_set: test data set
    :param y_set: test data set actual labels
    :param target_label: target label for confusion matrix calculation
    :param epsilon: maximum perturbation size
    :param adversarial_attack: adversarial attack used to generated samples
    :returns: quadruple containing confusion matrix differences in the form (% True Positive, % False Positive, % False Negative, % True Negative)
    """

    # Find the baseline confusion matrix
    (tp, fp, fn, tn) = get_confusion_matrix(classifier, x_set, y_set, target_label)

    # Generate an adversarial data set
    adv_crafter = adversarial_attack(classifier)
    x_test_adv = adv_crafter.generate(x=x_set, eps=epsilon)

    # Find the confusion matrix using adversarial data
    (tp_, fp_, fn_, tn_) = get_confusion_matrix(classifier, x_test_adv, y_set, target_label)

    # Return the differences for the two confusion matrices
    return tp - tp_, fp - fp_, fn - fn_, tn - tn_

def get_confusion_matrix_difference_preprocessed(classifier, x_set, y_set, target_label, epsilon, adversarial_attack, preprocessor):
    """
    Gets the differences in classification categories of an untampered data set and an adversarial data set generated using pre-processed data.

    :param classifier: ART Keras classifier
    :param x_set: test data set
    :param y_set: test data set actual labels
    :param target_label: target label for confusion matrix calculation
    :param epsilon: maximum perturbation size
    :param adversarial_attack: adversarial attack used to generated samples
    :param adversarial_attack: pre-processor based defense to apply to input data
    :returns: quadruple containing confusion matrix differences in the form (% True Positive, % False Positive, % False Negative, % True Negative)
    """

    # Find the baseline confusion matrix
    (tp, fp, fn, tn) = get_confusion_matrix(classifier, x_set, y_set, target_label)

    # Generate pre-processed input data
    preproc = preprocessor()
    preprocessed_x = preproc(x_set)

    # Generate an adversarial data set
    adv_crafter = adversarial_attack(classifier)
    x_test_adv = adv_crafter.generate(x=preprocessed_x, eps=epsilon)

    # Find the confusion matrix using adversarial data
    (tp_, fp_, fn_, tn_) = get_confusion_matrix(classifier, x_test_adv, y_set, target_label)

    # Return the differences for the two confusion matrices
    return tp - tp_, fp - fp_, fn - fn_, tn - tn_


def create_art_keras_classifier(model, min, max, x_set, y_set):
    """
    Converts a plain keras model into one which can be used by adversarial robustness toolbox

    :param model: plain keras model
    :param min: minimum label in test data set
    :param max: maximum label in test data set
    :param x_set: test data set
    :param y_set: test data set actual labels
    :returns: quadruple containing confusion matrix in the form (% True Positive, % False Positive, % False Negative, % True Negative)
    """
    art_keras_classifier = KerasClassifier((min, max), model=model)
    art_keras_classifier.fit(x_set, y_set, nb_epochs=1, batch_size=128)
    return art_keras_classifier
