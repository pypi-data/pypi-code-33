from abc import abstractmethod, ABCMeta
from copy import deepcopy
from itertools import tee
from collections import defaultdict, OrderedDict

import numpy as np
import pandas as pd
from scipy.stats import fisher_exact, chi2_contingency


class ModelBase(metaclass=ABCMeta):

    def __init__(self, params=None, **kwargs):
        self.params = params
        self._features = dict()
        self._labels = dict()
        self._str_features_topf = dict()
        self.topf = 0.5

    @abstractmethod
    def fit(self, X, Y):
        pass

    @abstractmethod
    def predict(self, X):
        pass

    @staticmethod
    @abstractmethod
    def _convert_str_to_factors():
        """
        Set if char type features must be converted into factors
        :return: bool
        """
        return bool()

    @abstractmethod
    def str_to_factors(self, X):
        pass

    @abstractmethod
    def validate(self, X_test, Y_test, labels_to_remove=None):
        pass

    @classmethod
    def optimize_params(cls,
                        X,
                        Y,
                        X_test,
                        Y_test,
                        var_params_grid,
                        constant_params=None,
                        eval_labels=None):

        best_params = dict((param, var_params_grid[param].pop(0)) for param in var_params_grid)
        if constant_params is not None:
            best_params.update(constant_params)
        model_0 = cls(params=deepcopy(best_params))
        if cls._convert_str_to_factors():
            X_eval = model_0.str_to_factors(X=X)
            X_test = model_0.str_to_factors(X=X_test)
        else:
            X_eval = X
        str_features_topf = model_0._str_features_topf
        X_eval, X_eval0 = tee(X_eval)
        X_test, X_test0 = tee(X_test)
        model_0.fit(X=X_eval0, Y=Y)
        confusion_matrix = model_0.validate(X_test=X_test0, Y_test=Y_test)[1]
        if type(eval_labels) in (list, tuple, set, frozenset):
            best_score = sum(confusion_matrix[label][label] for label in eval_labels)
        else:
            best_score = sum(confusion_matrix[label][label] for label in confusion_matrix.columns)
        for param in var_params_grid:
            print("'%s' parameter optimization started" % str(param))
            curr_params = deepcopy(best_params)
            for param_v in var_params_grid[param]:
                X_eval, X_evali = tee(X_eval)
                X_test, X_testi = tee(X_test)
                curr_params[param] = param_v
                model = cls(params=deepcopy(curr_params))
                model._str_features_topf = str_features_topf
                model.fit(X=X_evali, Y=Y)
                confusion_matrix = model.validate(X_test=X_testi, Y_test=Y_test)[1]
                if type(eval_labels) in (list, tuple, set, frozenset):
                    score = sum(confusion_matrix[label][label] for label in eval_labels)
                else:
                    score = sum(confusion_matrix[label][label] for label in confusion_matrix.columns)
                if score > best_score:
                    best_score = score
                    best_params[param] = param_v
            print("'%s' parameter optimization finished - optimal value: %s" % (str(param),
                                                                                str(best_params[param])))
        return best_params, best_score

    @abstractmethod
    def dump(self, scheme_path, **kwargs):
        pass

    @classmethod
    @abstractmethod
    def load(cls, scheme_path):
        pass

    @abstractmethod
    def get_features(self, X):
        pass

    @property
    @abstractmethod
    def features(self):
        pass

    @property
    @abstractmethod
    def labels(self):
        pass


class ArrayModelBase(ModelBase, metaclass=ABCMeta):

    @abstractmethod
    def fit(self, X, Y):
        """
        :param X: list or iterator of dicts with features {feat1: v1, feat2: v2, ...}
        :param Y: list of labels
        """
        if self._convert_str_to_factors():
            X = self.str_to_factors(X)
        X, Xf = tee(X)
        self.get_features(X=Xf)
        Y, Ys = tee(Y)
        labels_list = list(set(Ys))
        self._labels = dict((labels_list[i], i) for i in range(len(labels_list)))
        X = self.standardize_X(X=X)
        Y = map(lambda l: self._labels[l], Y)
        # train the model
        return X, Y  # this X and Y can be the input for train

    @abstractmethod
    def predict(self, X):
        """
        :param X: list or iterator of dicts with features {feat1: v1, feat2: v2, ...}
        :return: list of dicts with labels scores
        """
        if self._convert_str_to_factors():
            X = self.str_to_factors(X)
        X = self.standardize_X(X=X)
        # get and return the prediction result
        return X  # this X can be the input for predict

    def validate(self, X_test, Y_test, labels_to_remove=None):
        Y_test = np.stack(Y_test)
        tables_2x2 = defaultdict(lambda: defaultdict(int))
        test_pred = self.predict(X=X_test)
        labels = tuple(test_pred[0].keys())
        confusion_dict = OrderedDict()
        for label in labels:
            confusion_dict[label] = [0]*len(labels)
        confusion_matrix = pd.DataFrame.from_dict(data=confusion_dict, orient='index')
        confusion_matrix.columns = labels
        for i in range(len(test_pred)):
            not_TN = [Y_test[i]]
            prob_labels = get_prob_labels(test_pred[i], n_prob_states=1, max_d=0.1)
            if Y_test[i] in prob_labels:
                tables_2x2[Y_test[i]]["TP"] += 1
                confusion_matrix[Y_test[i]][Y_test[i]] += 1
            else:
                tables_2x2[Y_test[i]]["FN"] += 1
                tables_2x2[prob_labels[0]]["FP"] += 1
                confusion_matrix[prob_labels[0]][Y_test[i]] += 1
                not_TN.append(prob_labels[0])
            for label in test_pred[i]:
                if label not in not_TN:
                    tables_2x2[label]["TN"] += 1
        if type(labels_to_remove) in (list, tuple, set, frozenset):
            for label in labels_to_remove:
                del tables_2x2[label]
        tables_2x2_array = list()
        for label in tables_2x2.keys():
            tables_2x2_array.append([[tables_2x2[label]["TP"], tables_2x2[label]["FP"]],
                                     [tables_2x2[label]["FN"], tables_2x2[label]["TN"]]])
            tables_2x2[label]["Fisher_P-value"] = fisher_exact(tables_2x2_array[-1],
                                                               alternative='greater')[1]
            try:
                precision = float(tables_2x2[label]["TP"]) / float(tables_2x2[label]["TP"]+tables_2x2[label]["FP"])
                recall = float(tables_2x2[label]["TP"]) / float(tables_2x2[label]["TP"]+tables_2x2[label]["FN"])
                tables_2x2[label]["F1_score"] = 2.0 * (precision*recall) / (precision+recall)
            except ZeroDivisionError:
                tables_2x2[label]["F1_score"] = None
        tables_2x2["Chi-sq_P-value"] = chi2_contingency(tables_2x2_array)[1]
        return tables_2x2, confusion_matrix

    @abstractmethod
    def dump(self, scheme_path, **kwargs):
        pass

    @classmethod
    @abstractmethod
    def load(cls, scheme_path):
        pass

    def get_features(self, X):
        i = 0
        for x in X:
            for feat in x:
                if feat not in self._features:
                    self._features[feat] = i
                    i += 1

    def standardize_X(self, X):
        for x in X:
            feat_vals = list()
            for feat in self.features:
                feat_vals.append(x.get(feat, np.nan))
            yield np.array(feat_vals)

    @property
    def features(self):
        return list(map(lambda f: f[0], sorted(self._features.items(), key=lambda f: f[1])))

    @property
    def labels(self):
        return list(map(lambda l: l[0], sorted(self._labels.items(), key=lambda l: l[1])))

    @staticmethod
    @abstractmethod
    def _convert_str_to_factors():
        """
        Set if char type features must be converted into factors
        :return: bool
        """
        return bool()

    def str_to_factors(self, X):
        X, X0 = tee(X)
        if not self._str_features_topf:
            str_features = defaultdict(lambda: defaultdict(int))
            for x in X0:
                for feat in x:
                    if type(x[feat]) is str:
                        str_features[feat][x[feat]] += 1
            self._get_str_features_f50(str_features)
        for x in X:
            for feat in list(x.keys()):
                if type(x[feat]) is str:
                    x.update(self._fill_str_features(feat=feat,
                                                     feat_v=x[feat],
                                                     features_topf=self._str_features_topf[feat]))
                    del x[feat]
            yield x

    def _get_str_features_f50(self, str_features):
        for feat in str_features:
            features_topf = set()
            cur_sum = float()
            full_sum = sum(str_features[feat].values())
            for feat_item in sorted(str_features[feat].items(), key=lambda fi: fi[1], reverse=True):
                features_topf.add(feat_item[0])
                cur_sum += float(feat_item[1]) / float(full_sum)
                if cur_sum >= self.topf:
                    break
            if features_topf:
                self._str_features_topf[feat] = frozenset(features_topf)

    @staticmethod
    def _fill_str_features(feat, feat_v, features_topf):
        str_features = dict()
        for topf_feat_v in features_topf:
            if feat_v == topf_feat_v:
                str_features[feat + "_" + topf_feat_v] = True
            else:
                str_features[feat + "_" + topf_feat_v] = False
        return str_features


def get_prob_labels(labels_scores, n_prob_states=1, max_d=0.1):
    prob_labels = [(None, 0)]*n_prob_states
    for label in labels_scores:
        for i in range(n_prob_states):
            if i > 0:
                if prob_labels[i-1][1]-labels_scores[label] > max_d:
                    break
            if prob_labels[i][0] is None:
                prob_labels[i] = (label, labels_scores[label])
                break
            elif labels_scores[label]-prob_labels[i][1] > 0:
                prob_labels.insert(i, (label, labels_scores[label]))
                break
    return list(filter(None, map(lambda l: l[0], prob_labels[:n_prob_states])))
