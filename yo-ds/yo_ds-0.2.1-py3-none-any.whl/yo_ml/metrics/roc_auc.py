import numpy as np
from yo_extensions import *
from sklearn.metrics import roc_curve
from matplotlib import pyplot as plt


def _inner_roc_optimal_threshold(curve):
    dsts = curve[0] ** 2 + (1 - curve[1]) ** 2
    argmin = np.argmin(dsts)
    val = curve[2][argmin]
    return curve[0][argmin], curve[1][argmin], val

def roc_optimal_threshold(y_true, y_pred):
    curve = roc_curve(y_true, y_pred)
    _, __, val = _inner_roc_optimal_threshold(curve)
    return val

from yo_extensions.plots.infrastructure import PlotFactory

class roc_plot(PlotFactory):
    def __init__(self, true_column: str, predicted_column: str):
        super(roc_plot, self).__init__()
        self.true_column = true_column
        self.predicted_column = predicted_column

    def draw(self, obj: pd.DataFrame, ax: Axes):
        curve = roc_curve(obj[self.true_column],obj[self.predicted_column])
        ax.plot(curve[0],curve[1])
        ax.set_xlabel('TPR')
        ax.set_ylabel('FPR')
        x, y, val = _inner_roc_optimal_threshold(curve)
        ax.scatter(x,y)
        ax.text(x,y,str(val),ha='left',va='top')
