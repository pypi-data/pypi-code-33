import os
from sklearn.ensemble import RandomForestClassifier
from datasmash.quantizer import Quantizer, mkqdir, vectorize_label
from datasmash.utils import xgenesess
from datasmash.config import BIN_PATH


class XG1():
    """

    """
    def __init__(self, *, max_delay=20, classifier=None, multi_partition=True):
        xgenesess_path = os.path.join(BIN_PATH, 'XgenESeSS')
        assert os.path.isfile(xgenesess_path), "invalid bin path."

        self.tmp_dir = ''

        self.max_delay = max_delay
        self.quantizer = Quantizer(problem_type='supervised',
                                   multi_partition=multi_partition,
                                   featurization=xgenesess,
                                   featurization_params={'max_delay':
                                                         max_delay})

        if classifier is not None:
            self._classifier = classifier
        else:
            self._classifier = RandomForestClassifier(n_estimators=500,
                                                      max_depth=None,
                                                      min_samples_split=2,
                                                      random_state=0,
                                                      class_weight='balanced')
        self._fitted = False

    def fit(self, X, y):
        """

        """
        self.tmp_dir = mkqdir(X, labels=y, parent_dir='./')
        y_ = vectorize_label(X, y)
        X_ = self.quantizer.fit_transform(self.tmp_dir)
        self._classifier.fit(X_, y_)

        self._fitted = True

    def predict(self, X):
        """

        """
        X_ = self.quantizer.transform(X)
        predictions = self._classifier.predict(X_)
        return predictions

