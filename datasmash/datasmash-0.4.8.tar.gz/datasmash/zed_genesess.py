import os
from sklearn.ensemble import RandomForestClassifier
from datasmash.quantizer import Quantizer, mkqdir, vectorize_label
from datasmash.utils import genesess
from datasmash.config import BIN_PATH


class XG2():
    """

    """
    def __init__(self, *, depth=1000, classifier=None, multi_partition=True):
        genesess_path = os.path.join(BIN_PATH, 'genESeSS')
        assert os.path.isfile(genesess_path), "invalid bin path."

        self.tmp_dir = ''

        self.depth = depth
        self.quantizer = Quantizer(problem_type='supervised',
                                   multi_partition=multi_partition,
                                   featurization=genesess,
                                   featurization_params={'multi_line': True, 'depth': depth})

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

