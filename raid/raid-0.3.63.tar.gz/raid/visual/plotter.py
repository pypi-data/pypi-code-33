# -*- coding: utf-8 -*-

"""
<ENTER DESCRIPTION HERE>
"""

import os
import sys
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np
from k_vision import visual

from raid.logic.metric import Metric

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"

# Plot Settings.
C_MAP = "viridis"


class Plotter:

    @staticmethod
    def get_color_map(scheme: str, n_classes: int):
        """ Get a BGR uint (OpenCV format) color list for the map. """

        # To see what maps are available:
        # https://matplotlib.org/examples/color/colormaps_reference.html

        c_map = plt.get_cmap(scheme)
        color_dist = np.arange(n_classes)
        colors = c_map(1 - color_dist / (n_classes - 1))

        # Convert it to int BGR Lol.
        colors = [(int(c[2] * 255), int(c[1] * 255), int(c[0] * 255)) for c in colors]
        return colors

    @staticmethod
    def setup_plot():
        # Create the figure.
        plt.style.use("ggplot")
        fig, ax = plt.subplots(figsize=(9.6, 5.6))
        return fig, ax

    @staticmethod
    def save_distribution_map(
            path: str,
            distribution_map: [str, int],
            max_to_display: -1,
            color_scheme: str=None,
    ):

        fig, ax = Plotter.setup_plot()

        plot_cutoff = 20  # At what number amount to change the graph vis style.

        sorted_instances = sorted(distribution_map.items(), key=lambda kv: kv[1])
        sorted_instances.reverse()

        if max_to_display <= 0:
            max_to_display = sys.maxsize

        if max_to_display < len(sorted_instances):
            short_instances = sorted_instances[:max_to_display]
        else:
            short_instances = sorted_instances

        # Calibrate X and Y labels for the graph.
        x = [s[1] for s in short_instances]
        y_label = [s[0] for s in short_instances]

        if len(sorted_instances) > max_to_display:
            y_label.insert(0, "(OTHERS)")
            x.insert(0, sum([s[1] for s in sorted_instances[max_to_display:]]))
        y = np.arange(len(y_label))

        if color_scheme is None:
            color_scheme = C_MAP

        c_map = plt.get_cmap(color_scheme)
        colors = c_map(1 - y / (len(y) - 1))

        if len(sorted_instances) > max_to_display:
            colors[0] = (0.7, 0.7, 0.7, 1.0)

        # Plot the graph.
        bar_height = 0.8 if len(y) < plot_cutoff else 1.0
        plt.barh(y, x, height=bar_height, color=colors)

        if len(y) < plot_cutoff:
            ax.set_yticks(y)
            ax.set_yticklabels(y_label)

        ax.invert_yaxis()
        ax.set_title("Class Distribution")
        ax.set_xlabel("Count")
        ax.set_ylabel("Label")
        plt.savefig(path)
        plt.clf()
        plt.close()

    @staticmethod
    def render_metrics(metrics: Dict[str, Metric], output_dir: str):

        # # Generate colors and convert them to between 0-1 format.
        # colors = visual.generate_colors(len(metrics), as_numpy=True)
        # colors /= 255
        # colors = {k: colors[i] for i, k in enumerate(list(metrics.keys()))}

        color_index = 0
        for k, m in metrics.items():
            path = os.path.join(output_dir, f"{k}.png")
            Plotter.render_single_metric(m, path, f"C{color_index}")
            color_index += 1

        path = os.path.join(output_dir, f"all_metrics.png")
        Plotter.render_all_metrics(metrics, path)

    @staticmethod
    def render_single_metric(metric: Metric, path: str, color=None):
        fig, ax = Plotter.setup_plot()

        y = metric.aggregate_history
        x = np.arange(1, len(y) + 1)

        plt.plot(x, y, color=color)
        # plt.fill_between(x, y)
        plt.title(metric.title)

        # ax.set_xlim(x[0], x[-1])
        # ax.set_ylim(min(y), max(y))
        plt.savefig(path)
        plt.clf()
        plt.close()

    @staticmethod
    def render_all_metrics(metrics: Dict[str, Metric], path: str):
        fig, ax = Plotter.setup_plot()

        for k, m in metrics.items():

            y = m.aggregate_history

            # Normalize between 0 and 1
            y /= np.max(np.abs(y), axis=0)
            x = np.arange(1, len(y) + 1)
            plt.plot(x, y, label=k)

        ax.set_yticklabels([])
        ax.set_xticklabels([])

        plt.legend(loc='upper left')
        plt.savefig(path)
        plt.title("All Metrics")
        plt.clf()
        plt.close()
