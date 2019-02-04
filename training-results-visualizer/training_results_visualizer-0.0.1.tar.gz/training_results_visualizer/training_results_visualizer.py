from typing import Dict, Tuple, Callable, List
import numpy as np
import os
from sklearn.metrics import confusion_matrix, roc_curve, precision_recall_curve
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from seaborn import heatmap


class LearningVisualization:
    def __init__(self, graphs_per_row: int = 4):
        self._graphs_per_row = graphs_per_row

    def _get_history_values(self, value: str) -> np.array:
        h = np.array(self._history[value])
        return np.arange(h.size), h

    def _get_training_history_value(self, value: str) -> np.array:
        return self._get_history_values(value)

    def _get_testing_history_value(self, value: str) -> np.array:
        return self._get_history_values("val_{value}".format(value=value))

    def _get_model_history_values(self, value: str) -> np.array:
        return {
            "training": self._get_training_history_value(value),
            "testing": self._get_testing_history_value(value),
            "x_label": "Epoch"
        }

    def _get_roc_label(self, pred, true) -> np.array:
        return roc_curve(true, pred)[:2]

    def _get_prc_label(self, pred, true) -> np.array:
        return np.flip(precision_recall_curve(true, pred)[:2], axis=0)

    @property
    def accuracy(self):
        return {
            **self._get_model_history_values("acc"),
            "y_label": "Accuracy"
        }

    @property
    def loss(self):
        return {
            **self._get_model_history_values("loss"),
            "y_label": "Loss"
        }

    @property
    def roc(self):
        return {
            "training": self._get_roc_label(self._y_train_pred, self._y_train),
            "testing": self._get_roc_label(self._y_test_pred, self._y_test),
            "x_label": "False positive rate",
            "y_label": "True positive rate"
        }

    @property
    def prc(self):
        return {
            "training": self._get_prc_label(self._y_train_pred, self._y_train),
            "testing": self._get_prc_label(self._y_test_pred, self._y_test),
            "x_label": "Precision",
            "y_label": "Recall"
        }

    @property
    def confusion_matrices(self):
        return {
            "training":
            confusion_matrix(np.round(self._y_train_pred), self._y_train),
            "testing":
            confusion_matrix(np.round(self._y_test_pred), self._y_test)
        }

    @property
    def normalized_confusion_matrices(self):
        with np.errstate(divide='ignore', invalid='ignore'):
            return {
                "normalized {key}".format(key=key): np.nan_to_num(cm.astype(float)/cm.sum(axis=1)[:, np.newaxis])
                for key, cm in self.confusion_matrices.items()
            }

    def _plot(self, ax, graphs: Dict[str, Tuple[np.array, np.array]],
              name: str):
        ax.set_xlabel(graphs.pop("x_label"))
        ax.set_ylabel(graphs.pop("y_label"))
        for graph, (x, y) in graphs.items():
            ax.plot(
                x,
                y,
                label="{graph} {name}".format(
                    graph=graph.capitalize(), name=name))
        ax.grid()
        ax.set_title(name)

    def _heatmap(self, ax, matrix: np.array, name: str):
        heatmap(
            matrix,
            cmap="YlGnBu",
            cbar=False,
            annot=True,
            square=True,
            annot_kws={"size": 16},
            fmt="d" if matrix.dtype == "int" else "0.4g",
            ax=ax,
            xticklabels=self._labels,
            yticklabels=self._labels)
        ax.set_title(name)

    def _plots(self, title: str, structure: Dict, path: str,
               plotter: Callable):
        n = len(structure)
        size = 4
        row_size = min(n, self._graphs_per_row)
        column_size = np.ceil(n / row_size).astype(int)
        fig, axes = plt.subplots(column_size, row_size)
        fig.set_size_inches(size * row_size*1.1, size * column_size)
        sub_titles, graphs = zip(*list(structure.items()))
        [
            plotter(ax, graph, sub_title) for ax, graph, sub_title in zip(
                axes.reshape(-1), graphs, sub_titles)
        ]
        fig.suptitle(title, fontweight="bold")
        os.makedirs(path, exist_ok=True)
        plt.savefig("{path}/{title}.png".format(title=title, path=path))
        plt.close()

    def plot(self,
             history: np.array,
             y_train_pred: np.ndarray,
             y_test_pred: np.ndarray,
             y_train: np.array,
             y_test: np.array,
             labels: List[str],
             path: str = None):
        self._history = history
        self._y_train = y_train
        self._y_test = y_test
        self._y_train_pred = y_train_pred
        self._y_test_pred = y_test_pred
        self._labels = labels

        structures = {
            "Model history": {
                "Accuracy": self.accuracy,
                "Loss": self.loss
            },
            "Model curves": {
                "ROC": self.roc,
                "PRC": self.prc
            },
            "Confusion matrices": {
                **self.confusion_matrices,
                **self.normalized_confusion_matrices
            }
        }

        plotters = [self._plot, self._plot, self._heatmap]
        for (title, structure), plotter in zip(structures.items(), plotters):
            self._plots(title, structure, path, plotter)
