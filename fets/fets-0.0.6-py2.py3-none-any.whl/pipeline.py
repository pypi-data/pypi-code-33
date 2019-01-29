import pandas as pd
from sklearn.pipeline import Pipeline, FeatureUnion, _transform_one
from joblib import Parallel, delayed

class FeatureUnion2DF(FeatureUnion):
    """Default scikit learn FeatureUnion does not contacenate 
       the different transformers output into a dataframe.

       That is what FeatureUnion2DF does.

       inspired by Michele Lacchia (fixed in 2017-10-28):
       https://signal-to-noise.xyz/post/sklearn-pipeline/

       2018-12-02: Correction made as from scikit-learn 0.20.X _transform_one
       signature changed. _transform_one is an undocumented function.
    """
    def fit_transform(self, X, y=None, **fit_params):
        # non-optimized default implementation; override when a better
        # method is possible
        if y is None:
            # Unsupervised transformation
            return self.fit(X, **fit_params).transform(X)
        else:
            # Supervised transformation
            return self.fit(X, y, **fit_params).transform(X)

    def transform(self, X):
        # self._iter() gets the list of transformers in the (sub)pipeline
        # This is a generator of tuples such as:
        # ('tranform_NAME', transform_FUNCTION(factor=w), Weight(usually None))
        tr_names = [str(tr_name) for tr_name, trans, weight in self._iter()]

        # undocumented function _transform_one has changed from sklearn version 0.20.X:
        # def _transform_one(transformer, X, y, weight, **fit_params)
        #
        Xs = Parallel(n_jobs=self.n_jobs)(
            delayed(_transform_one)(trans, X, None, weight)
            for _, trans, weight in self._iter())

        N = 0
        for X, tr in zip(Xs, tr_names):
            # dataframe case
            if hasattr(X, "columns"):
                X.columns = ["f_"+col+"_"+tr for col in X.columns]   
            elif hasattr(X, "name"):
                X.name = "f"+str(N)+"_"+tr
                N += 1

        return pd.concat(Xs, axis=1, join='inner')

