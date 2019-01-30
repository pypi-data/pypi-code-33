#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Helper functions for visualizing data objects
"""

import colorsys
import os
import numpy as np
from sklearn.decomposition import PCA
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

# Use ggplot by default but user has the ability to change that
plt.style.use("ggplot")


def create_color_map(labels):
    """Maps label names to colors equidistant from each other

    Args:
        labels (set) -- The set of labels to create a color map for

    Returns:
        dict: The labels (keys) with assigned colors (values)
    """
    n = len(labels)
    HSV_tuples = [(x * 1.0 / n, .8, .8) for x in range(n)]
    RGB_tuples = list(map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples))
    return {label: RGB_tuples[i] for i, label in enumerate(labels)}


def plot_scatter(data, view, target, title=None, file_path=None, show=True, calculate_pca="2d"):
    """Plot a scatter plots of a particular view's principal components with a target used as the color.

    Args:
        data (DataObject): The DataObject to plot
        view (str): The name of the view to plot
        target (str): The name of the target to use for the color of the points on the plot
        title (str): The title on the plot
        file_path (str, optional): Defaults to None. The file path to save the image
        show (boolean, optional): Defaults to True. Show the resulting plot in matplotlib
        calculate_pca (str, optional): Defaults to "2d". Number of dimensions of the plot to produce if using PCA and whether to use PCA
    """
    # Always start by clearing previous figures
    plt.clf()

    # Determine available labels and label colors
    labels = set([str(item.targets[target]) for item in data])
    label_colors = create_color_map(labels)

    values = [item[view] for item in data.views]

    if calculate_pca == "2d" or len(values[0]) == 2:
        if calculate_pca == "2d":
            pca = PCA(n_components=2)
            values = pca.fit_transform(values)
        xs, ys = zip(*values)

        cols = [label_colors[item.targets[target]] for item in data]
        plt.scatter(xs, ys, c=cols)
        if title:
            plt.title(title)
        else:
            plt.title(view)
        if calculate_pca == "2d":
            plt.xlabel(f"PC1\n Explained Variance: {pca.explained_variance_ratio_[0]:.2f}")
            plt.ylabel(f"PC2\n Explained Variance: {pca.explained_variance_ratio_[1]:.2f}")
            plt.tight_layout()
        if file_path:
            dirs, _ = os.path.split(file_path)
            if not os.path.exists(dirs):
                os.makedirs(dirs)
            plt.savefig(file_path)
        if show:
            plt.show()

    elif calculate_pca == "3d" or len(values[0]) == 3:
        raise NotImplementedError("Not yet plotting in 3d.")
    else:
        raise ValueError("Entry for calculate_pca incompatible. Either bad option or data has more than 3 dimensions and no option selected.")


def plot_hist(data, view, target=None, title=None, file_path=None, show=True, calculate_pca=True):
    """Plot a scatter plots of a particular view's principal components with a target used as the color.

    Args:
        data (DataObject): The DataObject to plot
        view (str): The name of the view to plot
        target (str): The name of the target to plot, view must be set to None to plot a target
        title (str): The title on the plot
        file_path (str, optional): Defaults to None. The file path to save the image
        show (boolean, optional): Defaults to True. Show the resulting plot in matplotlib
        calculate_pca (str, optional): Defaults to True. Whether to use PCA or use a single dimension
    """
    # Always start by clearing previous figures
    plt.clf()

    if view:
        values = [item[view] for item in data.views]
    elif target:
        values = [item[target] for item in data.targets]
    else:
        raise ValueError("You must specify a view or target to plot")
    if view and target:
        raise ValueError("You must specify a view or target to plot. You cannot specify both")

    if calculate_pca:
        pca = PCA(n_components=1)
        values = pca.fit_transform(values)
    else:
        if hasattr(values[0], '__iter__'):
            raise ValueError("Provided view has more than one dimension and you selected to not calculate PCA. Unable to plot histogram.")

    plt.hist(values)

    if title:
        plt.title(title)
    if calculate_pca:
        plt.xlabel(f"PC1 of {view}\nExplained Variance: {pca.explained_variance_ratio_[0]:.2f}")
    else:
        plt.xlabel(view)

    if file_path:
        dirs, _ = os.path.split(file_path)
        if not os.path.exists(dirs):
            os.makedirs(dirs)
        plt.savefig(file_path)
    if show:
        plt.show()


def plot_joint(data, view, target, title=None, file_path=None, show=True, calculate_pca="2d"):
    """Plot a join plot (scatter + histograms) of a particular view's principal components with a target used as the color.

    Args:
        data (DataObject): The DataObject to plot
        view (str): The name of the view to plot
        target (str): The name of the target to use for the color of the points on the plot
        title (str): The title on the plot
        file_path (str, optional): Defaults to None. The file path to save the image
        show (boolean, optional): Defaults to True. Show the resulting plot in matplotlib
        calculate_pca (str, optional): Defaults to "2d". Number of dimensions of the plot to produce if using PCA and whether to use PCA
    """
    # Always start by clearing previous figures
    plt.clf()

    # Determine available labels and label colors
    labels = set([str(item.targets[target]) for item in data])
    label_colors = create_color_map(labels)

    values = [item[view] for item in data.views]

    if calculate_pca == "2d" or len(values[0]) == 2:
        if calculate_pca == "2d":
            pca = PCA(n_components=2)
            values = pca.fit_transform(values)
        xs, ys = zip(*values)

        cols = [label_colors[item.targets[target]] for item in data]

        fig, axScatter = plt.subplots()

        # the scatter plot:
        axScatter.scatter(xs, ys, c=cols)
        axScatter.set_aspect(1.)

        # create new axes on the right and on the top of the current axes
        # The first argument of the new_vertical(new_horizontal) method is
        # the height (width) of the axes to be created in inches.
        divider = make_axes_locatable(axScatter)
        axHistx = divider.append_axes("top", 1.2, pad=0.1, sharex=axScatter)
        axHisty = divider.append_axes("right", 1.2, pad=0.1, sharey=axScatter)

        # make some labels invisible
        axHistx.xaxis.set_tick_params(labelbottom=False)
        axHisty.yaxis.set_tick_params(labelleft=False)

        axHistx.hist(xs)
        axHisty.hist(ys, orientation='horizontal')

        plt.xlabel("")
        plt.ylabel("")
        plt.title("")

        if title:
            axHistx.set_title(title)
        else:
            axHistx.set_title(view)
        if calculate_pca == "2d":
            axScatter.set_xlabel(f"PC1\n Explained Variance: {pca.explained_variance_ratio_[0]:.2f}")
            axScatter.set_ylabel(f"PC2\n Explained Variance: {pca.explained_variance_ratio_[1]:.2f}")
            plt.tight_layout()
        else:
            axScatter.set_xlabel("x")
            axScatter.set_ylabel("y")
        if file_path:
            dirs, _ = os.path.split(file_path)
            if not os.path.exists(dirs):
                os.makedirs(dirs)
            plt.savefig(file_path)
        if show:
            plt.show()

    elif calculate_pca == "3d" or len(values[0]) == 3:
        raise NotImplementedError("Not yet plotting in 3d.")
    else:
        raise ValueError("Entry for calculate_pca incompatible. Either bad option or data has more than 3 dimensions and no option selected.")
