"""Code for running machine learning experiments
"""

import pandas as pd
import sklearn
from sklearn.model_selection import GridSearchCV


def run_sl(data, estimators, scoring, target, view=None):
    """Run supervised learning experiments comparing multiple estimators' target prediction on a particular view

    Args:
        data (DataObject): The data to train on
        estimators (iterable): an iterable containing dictionaries of the form {'name':estimator name, estimator': estimator, 'parameters': param_grid}.
        scoring (str or sklearn.scorer): The scoring method for running the gridsearch
        target (str): The target to predict
        view (str, optional): Defaults to None. The view with the features to use for the experiment. None will use the DataObject value.
    """
    train_view = [item[view] for item in data.views]
    train_target = [item[target] for item in data.targets]
    bestEstimators = [GridSearchCV(estimator["estimator"], estimator["parameters"], scoring=scoring).fit(
        train_view, train_target) for estimator in estimators]

    all_results = pd.DataFrame([
        {
            "Estimator": estimator["name"],
            "Score": bestEstimators[i].best_score_,
            "Std Dev": bestEstimators[i].cv_results_['std_test_score'][bestEstimators[i].best_index_],
            "est": bestEstimators[i].best_estimator_,
            "params": bestEstimators[i].best_params_,
        } for i, estimator in enumerate(estimators)
    ])

    results = all_results[["Estimator", "Score", "Std Dev"]]

    return results.to_latex(index=False), all_results


def run_mv_sl(data, estimators, scoring, target, views):
    """Run supervised learning experiments comparing multiple estimators' target prediction using different views

    Args:
        data (DataObject): The data to train on
        estimators (iterable): an iterable containing dictionaries of the form {'name':estimator name, estimator': estimator, 'parameters': param_grid}.
        scoring (str or sklearn.scorer): The scoring method for running the gridsearch
        target (str): The target to predict
        views (iterable): The views with the features to use for the experiment. None will use the DataObject value.
    """
    extracted_results = [run_sl(data, estimators, scoring, target, view)[1] for view in views]
    all_results = None

    for i, df in enumerate(extracted_results):
        df.insert(loc=0, column="View", value=[views[i]] * len(df.index))
        if all_results is not None:
            all_results = all_results.append(df)
        else:
            all_results = df

    results = all_results[["View", "Estimator", "Score", "Std Dev"]]
    results["Value"] = results.apply(lambda x: f"{x['Score']:2.3} \pm {2 * x['Std Dev']:2.3}", axis=1)
    results = results.pivot(index="View", columns="Estimator", values="Value")

    return results.to_latex(escape=False), all_results
