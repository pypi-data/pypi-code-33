#!/usr/bin/env python
"""Classification output analysis functions and classes"""
########################################################################
# File: classification.py
#  executable: classification.py
#
# Author: Andrew Bailey
# History: 12/19/18 Created
########################################################################

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from itertools import cycle

from sklearn.metrics import roc_curve, auc, confusion_matrix
from sklearn.metrics.ranking import _binary_clf_curve as binary_clf_curve
from sklearn.metrics import brier_score_loss
from sklearn.calibration import calibration_curve
from sklearn import preprocessing

from scipy import interp
from py3helpers.utils import binary_search


class ClassificationMetrics(object):

    def __init__(self, binary_labels, class_probabilities, class_ns=None):
        """Initialize binary labels and class probabilities"""
        assert isinstance(binary_labels, pd.DataFrame), \
            "binary_labels must be a pandas dataframe: type {}".format(type(binary_labels))
        assert isinstance(class_probabilities, pd.DataFrame), \
            "class_probabilities must be a pandas dataframe: type {}".format(type(class_probabilities))

        self.fps = dict()
        self.tps = dict()
        self.fns = dict()
        self.tns = dict()

        self.fpr = dict()
        self.tpr = dict()
        self.fnr = dict()
        self.tnr = dict()
        self.ppv = dict()
        self.fdr = dict()
        self.for1 = dict()
        self.npv = dict()
        self.thresholds = dict()
        self.roc_auc = dict()

        self.total = 0
        self.class_totals = dict()

        self.binary_labels = binary_labels
        self.class_probabilities = class_probabilities
        self.class_ns = class_ns
        self.n_classes = 0
        self._set_check_class_ns()
        self._calculate_fp_tp_rate()

    def _set_check_class_ns(self):
        """Check class names from input data and optional argument

        Note: if class_ns is not passed in then we will will throw error
        """
        if self.class_ns is None:
            tmp_class_ns = [str(x) for x in self.binary_labels.dtypes.index]
            tmp_class_ns_2 = [str(x) for x in self.class_probabilities.dtypes.index]
            assert tmp_class_ns == tmp_class_ns_2, \
                "binary_labels and class_probabilities must have same column names: " \
                "binary_labels - {}, class_probabilities - {}".format(tmp_class_ns, tmp_class_ns_2)
            self.class_ns = tmp_class_ns
        assert len(self.class_ns) == self.binary_labels.shape[1]
        assert len(self.class_ns) == self.class_probabilities.shape[1]
        self.n_classes = len(self.class_ns)

    def _calculate_fp_tp_rate(self):
        """Calculate false positives and true positive rates"""
        # Compute false and true positives, ROC data and other important binary classification metrics
        for class_n in self.class_ns:
            self.fps[class_n], self.tps[class_n], self.thresholds[class_n] = \
                binary_clf_curve(self.binary_labels[class_n], self.class_probabilities[class_n])
            if self.tps[class_n].size == 0 or self.fps[class_n][0] != 0:
                # Add an extra threshold position if necessary
                self.tps[class_n] = np.r_[0, self.tps[class_n]]
                self.fps[class_n] = np.r_[0, self.fps[class_n]]
                self.thresholds[class_n] = np.r_[self.thresholds[class_n][0] + 1, self.thresholds[class_n]]

            self.fns[class_n] = self.tps[class_n][-1] - self.tps[class_n]
            self.tns[class_n] = self.fps[class_n][-1] - self.fps[class_n]
            # positive predictive value
            self.ppv[class_n] = self.tps[class_n] / (self.tps[class_n] + self.fps[class_n])
            # false discovery rate
            self.fdr[class_n] = self.fps[class_n] / (self.tps[class_n] + self.fps[class_n])
            # negative predictive value
            self.npv[class_n] = self.tns[class_n] / (self.tns[class_n] + self.fns[class_n])
            # false omission rate
            self.for1[class_n] = self.fns[class_n] / (self.tns[class_n] + self.fns[class_n])

            # true/false positive/negative rates
            self.fpr[class_n] = self.fps[class_n] / self.fps[class_n][-1]
            self.tpr[class_n] = self.tps[class_n] / self.tps[class_n][-1]
            self.tnr[class_n] = 1 - self.fpr[class_n]
            self.fnr[class_n] = 1 - self.tpr[class_n]

            self.roc_auc[class_n] = auc(self.fpr[class_n], self.tpr[class_n])

        self.fpr["micro"], self.tpr["micro"], self.thresholds["micro"] = \
            roc_curve(self.binary_labels.values.ravel(), self.class_probabilities.values.ravel())
        self.tnr["micro"] = 1 - self.fpr["micro"]
        self.fnr["micro"] = 1 - self.tpr["micro"]
        self.roc_auc["micro"] = auc(self.fpr["micro"], self.tpr["micro"])

        all_fpr = np.unique(np.concatenate([self.fpr[i] for i in self.class_ns]))

        # Then interpolate all ROC curves at this points
        mean_tpr = np.zeros_like(all_fpr)
        for class_n in self.class_ns:
            mean_tpr += interp(all_fpr, self.fpr[class_n], self.tpr[class_n])

        # Finally average it and compute AUC
        mean_tpr /= self.n_classes

        self.fpr["macro"] = all_fpr
        self.tpr["macro"] = mean_tpr
        self.tnr["macro"] = 1 - self.fpr["macro"]
        self.fnr["macro"] = 1 - self.tpr["macro"]

        self.roc_auc["macro"] = auc(self.fpr["macro"], self.tpr["macro"])

    def _get_index_from_threshold(self, class_n, threshold):
        """Get correct index from any arbitrary probability threshold cutoff"""
        assert class_n in self.class_ns, \
            "Class name is not in class names. {} not in {}".format(class_n, self.class_ns)
        index = binary_search(self.thresholds[class_n][::-1], threshold, exact_match=False)
        if index == len(self.thresholds[class_n]) - 1:
            return 0
        elif index == 0:
            return len(self.thresholds[class_n]) - 1
        else:
            return len(self.thresholds[class_n]) - index - 2

    def plot_roc(self, class_n, save_fig_path=None):
        if save_fig_path is not None:
            assert os.path.exists(os.path.dirname(save_fig_path)), \
                "Output directory does not exist: {}".format(save_fig_path)

        plt.figure()
        lw = 2
        plt.plot(self.fpr[class_n], self.tpr[class_n], color='darkorange',
                 lw=lw, label='ROC curve (area = %0.2f)' % self.roc_auc[class_n])
        plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver operating characteristic example')
        plt.legend(loc="lower right")
        if save_fig_path is not None:
            plt.savefig(save_fig_path)
        else:
            plt.show()
            pass

    def plot_multiclass_roc(self, lw=2, save_fig_path=None):
        # Plot all ROC curves
        if save_fig_path is not None:
            assert os.path.exists(os.path.dirname(save_fig_path)), \
                "Output directory does not exist: {}".format(save_fig_path)

        plt.figure()
        plt.plot(self.fpr["micro"], self.tpr["micro"],
                 label='micro-average ROC curve (area = {0:0.2f})'
                       ''.format(self.roc_auc["micro"]),
                 color='deeppink', linestyle=':', linewidth=4)

        plt.plot(self.fpr["macro"], self.tpr["macro"],
                 label='macro-average ROC curve (area = {0:0.2f})'
                       ''.format(self.roc_auc["macro"]),
                 color='navy', linestyle=':', linewidth=4)

        colors = cycle(['aqua', 'darkorange', 'cornflowerblue'])
        for i, color in zip(self.class_ns, colors):
            plt.plot(self.fpr[i], self.tpr[i], color=color, lw=lw,
                     label='ROC curve of class {0} (area = {1:0.2f})'
                           ''.format(i, self.roc_auc[i]))

        plt.plot([0, 1], [0, 1], 'k--', lw=lw)
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Some extension of Receiver operating characteristic to multi-class')
        plt.legend(loc="lower right")
        if save_fig_path is not None:
            plt.savefig(save_fig_path)
        else:
            plt.show()
            pass

    def recall(self, class_n, threshold):
        return self.true_positive_rate(class_n, threshold)

    def sensitivity(self, class_n, threshold):
        return self.true_positive_rate(class_n, threshold)

    def specificity(self, class_n, threshold):
        return self.true_negatives_rate(class_n, threshold)

    def true_positive_rate(self, class_n, threshold):
        return self.tpr[class_n][self._get_index_from_threshold(class_n, threshold)]

    def false_positive_rate(self, class_n, threshold):
        return self.fpr[class_n][self._get_index_from_threshold(class_n, threshold)]

    def true_negatives_rate(self, class_n, threshold):
        return self.tnr[class_n][self._get_index_from_threshold(class_n, threshold)]

    def false_negatives_rate(self, class_n, threshold):
        return self.fnr[class_n][self._get_index_from_threshold(class_n, threshold)]

    def positive_likelihood_ratio(self, class_n, threshold):
        fpr = self.false_positive_rate(class_n, threshold)
        tpr = self.true_positive_rate(class_n, threshold)
        return tpr/fpr

    def negative_likelihood_ratio(self, class_n, threshold):
        fpr = self.false_positive_rate(class_n, threshold)
        tpr = self.true_positive_rate(class_n, threshold)
        return fpr/tpr

    def diagostic_odds_ratio(self, class_n, threshold):
        plr = self.positive_likelihood_ratio(class_n, threshold)
        nlr = self.negative_likelihood_ratio(class_n, threshold)
        return plr/nlr

    def positive_predictive_value(self, class_n, threshold):
        return self.ppv[class_n][self._get_index_from_threshold(class_n, threshold)]

    def precision(self, class_n, threshold):
        return self.positive_predictive_value(class_n, threshold)

    def false_discovery_rate(self, class_n, threshold):
        return self.fdr[class_n][self._get_index_from_threshold(class_n, threshold)]

    def negative_predictive_value(self, class_n, threshold):
        return self.npv[class_n][self._get_index_from_threshold(class_n, threshold)]

    def false_omission_rate(self, class_n, threshold):
        return self.for1[class_n][self._get_index_from_threshold(class_n, threshold)]

    def f1_score(self, class_n, threshold):
        precision = self.precision(class_n, threshold)
        recall = self.recall(class_n, threshold)
        return 2 / ((1/precision) + (1/recall))

    def prevalence(self, class_n):
        return np.count_nonzero(self.binary_labels[class_n])

    def confusion_matrix(self):
        labels = self.binary_labels.idxmax(1)
        predictions = self.class_probabilities.idxmax(1)
        return confusion_matrix(labels, predictions, labels=self.class_ns)

    def plot_calibration_curve(self, class_n, save_fig_path=None):
        if save_fig_path is not None:
            assert os.path.exists(os.path.dirname(save_fig_path)), \
                "Output directory does not exist: {}".format(save_fig_path)

        labels = self.binary_labels[class_n]
        predictions = self.class_probabilities[class_n]
        clf_score = brier_score_loss(labels, predictions)
        fraction_of_positives, mean_predicted_value = \
            calibration_curve(labels, predictions, n_bins=10)

        plt.figure(figsize=(10, 10))
        ax1 = plt.subplot2grid((3, 1), (0, 0), rowspan=2)
        ax2 = plt.subplot2grid((3, 1), (2, 0))

        ax1.plot([0, 1], [0, 1], "k:", label="Perfectly calibrated")

        ax1.plot(mean_predicted_value, fraction_of_positives, "s-",
                 label="%s (%1.3f)" % (class_n, clf_score))

        ax2.hist(predictions, range=(0, 1), bins=10, label=class_n,
                 histtype="step", lw=2)
        ax1.set_ylabel("Fraction of positives")
        ax1.set_ylim([-0.05, 1.05])
        ax1.legend(loc="lower right")
        ax1.set_title('Calibration plots  (reliability curve)')

        ax2.set_xlabel("Mean predicted value")
        ax2.set_ylabel("Count")
        ax2.legend(loc="upper center", ncol=2)
        if save_fig_path is not None:
            plt.savefig(save_fig_path)
        else:
            plt.show()
            pass

