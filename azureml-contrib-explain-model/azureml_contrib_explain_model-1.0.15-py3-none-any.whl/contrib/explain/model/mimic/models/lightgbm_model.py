# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines an explainable lightgbm model."""

from .explainable_model import BaseExplainableModel
from lightgbm import LGBMRegressor, LGBMClassifier
import shap

DEFAULT_RANDOM_STATE = 123


class LGBMExplainableModel(BaseExplainableModel):
    """The base class for models that can be explained."""

    def __init__(self, multiclass=False, random_state=DEFAULT_RANDOM_STATE, **kwargs):
        """Initialize the LightGBM Model."""
        super(LGBMExplainableModel, self).__init__(**kwargs)
        self._logger.debug('Initializing LGBMExplainableModel')
        self.multiclass = multiclass
        if self.multiclass:
            self.lgbm = LGBMClassifier(random_state=random_state)
        else:
            self.lgbm = LGBMRegressor(random_state=random_state)

    def fit(self, dataset, labels, **kwargs):
        """Call lightgbm fit to fit the explainable model."""
        self.lgbm.fit(dataset, labels)

    def predict(self, dataset, **kwargs):
        """Call lightgbm predict to predict labels using the explainable model."""
        return self.lgbm.predict(dataset)

    def predict_proba(self, dataset, **kwargs):
        """Call lightgbm predict_proba to predict probabilities using the explainable model."""
        if self.multiclass:
            return self.lgbm.predict_proba(dataset)
        else:
            raise Exception("predict_proba not supported for regression or binary classification dataset")

    def explain_global(self, **kwargs):
        """Call feature_importances_ to get the global feature importances from the explainable model.

        :return: The global explanation of feature importances.
        :rtype: list
        """
        return self.lgbm.feature_importances_

    def explain_local(self, evaluation_examples, **kwargs):
        """Use TreeExplainer to get the local feature importances from the trained explainable model.

        :return: The local explanation of feature importances.
        :rtype: Union[list, numpy.ndarray]
        """
        tree_explainer = shap.TreeExplainer(self.lgbm)
        return tree_explainer.shap_values(evaluation_examples)

    @property
    def model(self):
        """Retrieve the underlying model.

        :return: The lightgbm model, either classifier or regressor.
        :rtype: Union[LGBMClassifier, LGBMRegressor]
        """
        return self.lgbm
