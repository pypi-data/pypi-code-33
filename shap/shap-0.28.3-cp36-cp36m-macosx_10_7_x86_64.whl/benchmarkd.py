import sklearn
import numpy as np


def holdout3(X, y, Xt, yt, model_generator, methods, metric):
    """ The holdout evaluation metric compares performance when important features are removed.

    sklearn.metrics.r2_score
    """

    _curve_benchmark(
        X, y, Xt, yt, model_generator, methods,
        _holdout_fraction, True, nfractions, metric
    )

def plot_scores(fractions, methods, show=True):

    # eval each fraction
    fractions = np.linspace(0, 1, nfractions)
    vals = []
    for (name,At) in methods:
        vals.append(np.array([eval_method(f, X, y, Xt, yt, At, model_generator, metric) for f in fractions]))

    # make a plot of the results
    for (name,scores) in methods:
        pl.plot(fractions, scores, label=name)
    pl.xlabel("Fraction of features")
    if negate:
        pl.ylabel("1 - R-squared")
    else:
        pl.ylabel("R-squared")
    pl.title(eval_method.__name__ + " on " + gen_model.__name__ + " model")
    pl.legend()
    pl.show()

def holdout(fraction, X, y, Xt, yt, At, model_generator, metric):

    def to_array(*args):
        return [a.values if str(type(a)).endswith("'pandas.core.frame.DataFrame'>") else a for a in args]
    X, Xt = to_array(X, Xt)

    # how many features to mask
    nmask = int(fraction * X.shape[1])

    # If needed, train a model and compute the predictions without masking
    if nmask == 0:
        model = model_generator()
        model.fit(X, y)
        yp = model.predict(Xt)
        return metric(yt, yp)

    # mask nmask top features and re-train the model for each test explanation
    X_tmp = np.zeros(X.shape)
    Xt_tmp = np.zeros(Xt.shape)
    yp_mod = np.zeros(yt.shape)
    for i in range(len(yt)):

        # mask out the most important features for this test instance
        X_tmp[:] = X
        Xt_tmp[:] = Xt
        ordering = np.argsort(-At[i,:])
        X_tmp[:,ordering[:nmask]] = X[:,ordering[:nmask]].mean()
        Xt_tmp[:,ordering[:nmask]] = X[:,ordering[:nmask]].mean()

        # retrain the model and make a prediction
        model_masked = model_generator()
        model_masked.fit(X_tmp, y)
        yp_mod[i] = model_masked.predict(Xt_tmp[i:i+1])[0]

    return metric(yt, yp_mod)
