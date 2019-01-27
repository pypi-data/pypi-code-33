from concurrent.futures import ProcessPoolExecutor
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from treeinterpreter import treeinterpreter as ti


def parallel_trees(m, fn, n_jobs=8):
    return list(ProcessPoolExecutor(n_jobs).map(fn, m.estimators_))


def get_ensamble_preds(model, x):
    """Return separately the predictions done by all the estimators in ensemble.

    Parameters
    ----------
    model
    x

    Returns
    -------
    predictions : ndarray shaped (estimators, n_samples)
    """
    # TODO: figure out how to get the faster version commented below working
    # (AttributeError: Can't pickle local object 'get_ensamble_preds.<locals>.get_preds')
    # def get_preds(t):
    #     return t.predict(x)
    #
    # return np.stack(parallel_trees(model, get_preds))

    # WORKAROUND for large datasets:
    # run code above manually (eg. in script.notebook), then use
    # make_ensemble_preds_with_confidence_table directly instead of get_ensemble_preds_with_confidence

    return np.stack([t.predict(x) for t in model.estimators_])


def make_ensemble_preds_with_confidence_table(df_raw_val, preds, fld, y_fld):
    df = df_raw_val.copy()

    df['pred_std'] = np.std(preds, axis=0)
    df['pred'] = np.mean(preds, axis=0)

    flds = [fld, y_fld, 'pred', 'pred_std']
    tbl = df[flds].groupby(flds[0], as_index=False).mean()

    return tbl


def get_ensemble_preds_with_confidence(
        model, x_val, df_raw_val, fld, y_fld
):
    preds = get_ensamble_preds(model, x_val)
    return make_ensemble_preds_with_confidence_table(df_raw_val, preds, fld, y_fld)


# TODO: confirm this works
def plot_ensemble_regression_preds_with_confidence(
        model, x_val, df_raw_val, fld, y_fld, figsize=None
):
    preds = get_ensamble_preds(model, x_val)
    tbl = make_ensemble_preds_with_confidence_table(df_raw_val, preds, fld, y_fld)
    return tbl.plot(tbl, 'pred', 'barh',
                    xerr='pred_std', alpha=0.6, figsize=figsize)


def rf_feat_importance(model, df):
    return pd.DataFrame(
        {'cols': df.columns, 'imp': model.feature_importances_}
    ).sort_values('imp', ascending=False)


def rf_show_plot_fi(model, df, figsize=(12,7), top_n=None):
    fi = rf_feat_importance(model, df)
    if top_n:
        fi = fi[:top_n]
    print(fi)
    fi.plot('cols', 'imp', 'barh', figsize=figsize, legend=False)


def ti_make_readable_contribs(df, cs):
    idxs = np.argsort(cs[:, 0])
    sorted_feats = df.columns[idxs]
    return [o for o in zip(
        sorted_feats,
        df.iloc[0][sorted_feats],
        cs[idxs],
    )]


def ti_make_explained_predictions_data(df, preds, contribs):
    xcontribs = [ti_make_readable_contribs(df, c) for c in contribs]
    preds_dict = [{
        i : p
        for i, p in enumerate(pred)
    } for pred in preds]
    return list(zip(preds_dict, xcontribs))


def rf_predict_with_explanations(model, x):
    preds, biases, contribs = ti.predict(model, x)
    return ti_make_explained_predictions_data(x, preds, contribs)


def plot_train_vs_test(
        model, x, y,
        trn_f=0.8, n_runs=5, step=50, start=None,
        ylim=None
):
    if start is None:
        start = step
    extra_plot_args = {'ylim': ylim} if ylim else {}
    test_size = int(len(x) * (1 - trn_f))
    train_sizes = list(range(start, int(x.shape[0] * trn_f), step))
    scores_trn = np.zeros((3, len(train_sizes)))
    scores_val = np.zeros((3, len(train_sizes)))
    s_trn = np.zeros(n_runs)
    s_val = np.zeros(n_runs)
    for i, train_sz in enumerate(train_sizes):
        for j in range(n_runs):
            x_trn, x_val, y_trn, y_val = train_test_split(
                x, y, test_size=test_size)
            x_trn = x_trn[:train_sz]
            y_trn = y_trn[:train_sz]
            model.fit(x_trn, y_trn)
            s_trn[j] = model.score(x_trn, y_trn)
            s_val[j] = model.score(x_val, y_val)
        scores_trn[0, i] = np.mean(s_trn)
        scores_trn[1, i] = np.min(s_trn)
        scores_trn[2, i] = np.max(s_trn)
        scores_val[0, i] = np.mean(s_val)
        scores_val[1, i] = np.min(s_val)
        scores_val[2, i] = np.max(s_val)
        s_trn[:] = 0
        s_val[:] = 0
    if ylim is not None:
        axes = plt.gca()
        axes.set_ylim(ylim)
    plt.plot(train_sizes, scores_trn[0, :], color='b', label='train')
    plt.fill_between(
        train_sizes, scores_trn[1, :], scores_trn[2, :],
        facecolor='b', alpha=0.4)
    plt.plot(train_sizes, scores_val[0, :], color='r', label='test')
    plt.fill_between(
        train_sizes, scores_val[1, :], scores_val[2, :],
        facecolor='r', alpha=0.4)
    plt.xlabel('train sz')
    plt.ylabel('score')
    plt.legend()


def plot_train_vs_test_by_param(
        model_costructor, model_params, param_name, param_vals, x, y,
        trn_f=0.8, n_runs=10
):
    model_params = model_params.copy()

    test_size = int(len(x) * (1 - trn_f))

    scores_trn = np.zeros((3, len(param_vals)))
    scores_val = np.zeros((3, len(param_vals)))

    s_trn = np.zeros(n_runs)
    s_val = np.zeros(n_runs)

    for i, val in enumerate(param_vals):
        for j in range(n_runs):
            x_trn, x_val, y_trn, y_val = train_test_split(
                x, y, test_size=test_size)

            model = model_costructor(**model_params, **{param_name: val})
            model.fit(x_trn, y_trn)

            s_trn[j] = model.score(x_trn, y_trn)
            s_val[j] = model.score(x_val, y_val)

        scores_trn[0, i] = np.mean(s_trn)
        scores_trn[1, i] = np.min(s_trn)
        scores_trn[2, i] = np.max(s_trn)
        scores_val[0, i] = np.mean(s_val)
        scores_val[1, i] = np.min(s_val)
        scores_val[2, i] = np.max(s_val)
        s_trn[:] = 0
        s_val[:] = 0

    plt.plot(param_vals, scores_trn[0, :], color='b', label='train')
    plt.fill_between(
        param_vals, scores_trn[1, :], scores_trn[2, :],
        facecolor='b', alpha=0.4)
    plt.plot(param_vals, scores_val[0, :], color='r', label='test')
    plt.fill_between(
        param_vals, scores_val[1, :], scores_val[2, :],
        facecolor='r', alpha=0.4)
    plt.ylabel('score')
    plt.xlabel(param_name)
    plt.legend()