#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from ex4ml import viz
from ex4ml.objects.dataobject import DataObject
import os
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')


def test_plot_scatter():
    # Setup data
    view1 = {
        "A": [4, 3],
        "B": [5, 2, 7],
    }
    target1 = {
        "Label": "Label 1"
    }

    view2 = {
        "A": [2, 3],
        "B": [2, 1, 3],
    }
    target2 = {
        "Label": "Label 2"
    }

    view3 = {
        "A": [2, 0],
        "B": [3, 4, 18],
    }
    target3 = {
        "Label": "Label 3"
    }

    view4 = {
        "A": [2, 15],
        "B": [10, 4, 15],
    }
    target4 = {
        "Label": "Label 4"
    }

    view5 = {
        "A": [2, 10],
        "B": [33, 4, 24],
    }
    target5 = {
        "Label": "Label 3"
    }

    view6 = {
        "A": [22, 0],
        "B": [13, 14, 9],
    }
    target6 = {
        "Label": "Label 5"
    }

    # Format data
    views = [view1, view2, view3, view4, view5, view6]
    targets = [target1, target2, target3, target4, target5, target6]

    do = DataObject([None] * len(views), views=views, targets=targets)

    # Plot data
    viz.plot_scatter(do, "A", "Label", "A", show=False, calculate_pca=False)
    plt.xlabel("x")
    plt.ylabel("y")
    fp = "images/tests/scatter.png"
    dirs, _ = os.path.split(fp)
    if not os.path.exists(dirs):
        os.makedirs(dirs)
    plt.savefig(fp)

    # Plot PCA
    viz.plot_scatter(do, "B", "Label", "B", "images/tests/pca_scatter.png", show=False)

    # Try out another style
    plt.style.use("seaborn")
    viz.plot_scatter(do, "B", "Label", "Seaborn B", "images/tests/pca_scatter_seaborn.png", show=False)

    # Reset plotting style
    plt.style.use("ggplot")


def test_plot_hist():
    # Setup data
    view1 = {
        "A": 4,
        "B": [5, 2, 7],
    }
    target1 = {
        "Label": 1
    }

    view2 = {
        "A": 2,
        "B": [2, 1, 3],
    }
    target2 = {
        "Label": 1
    }

    view3 = {
        "A": 2,
        "B": [3, 4, 18],
    }
    target3 = {
        "Label": 1
    }

    view4 = {
        "A": 2,
        "B": [10, 4, 15],
    }
    target4 = {
        "Label": 2
    }

    view5 = {
        "A": 2,
        "B": [33, 4, 24],
    }
    target5 = {
        "Label": 2
    }

    view6 = {
        "A": 22,
        "B": [13, 14, 9],
    }
    target6 = {
        "Label": 3
    }

    # Format data
    views = [view1, view2, view3, view4, view5, view6]
    targets = [target1, target2, target3, target4, target5, target6]

    do = DataObject([None] * len(views), views=views, targets=targets)

    # Plot single data
    viz.plot_hist(do, "A", title="A", show=False, calculate_pca=False)
    plt.xlabel("x")
    fp = "images/tests/hist.png"
    dirs, _ = os.path.split(fp)
    if not os.path.exists(dirs):
        os.makedirs(dirs)
    plt.savefig(fp)

    # Plot PCA hist
    viz.plot_hist(do, "B", file_path="images/tests/pca_hist.png", show=False)

    # Plot target hist
    viz.plot_hist(do, None, target="Label", file_path="images/tests/target_hist.png", show=False, calculate_pca=False)

    # Plot with searborn
    plt.style.use("seaborn")
    viz.plot_hist(do, "B", file_path="images/tests/seaborn_pca_hist.png", show=False)

    # Reset plotting style
    plt.style.use("ggplot")


def test_plot_joint():
    # Setup data
    view1 = {
        "A": [4, 3],
        "B": [5, 2, 7],
    }
    target1 = {
        "Label": "Label 1"
    }

    view2 = {
        "A": [2, 3],
        "B": [2, 1, 3],
    }
    target2 = {
        "Label": "Label 2"
    }

    view3 = {
        "A": [2, 0],
        "B": [3, 4, 18],
    }
    target3 = {
        "Label": "Label 3"
    }

    view4 = {
        "A": [2, 15],
        "B": [10, 4, 15],
    }
    target4 = {
        "Label": "Label 4"
    }

    view5 = {
        "A": [2, 10],
        "B": [33, 4, 24],
    }
    target5 = {
        "Label": "Label 3"
    }

    view6 = {
        "A": [22, 0],
        "B": [13, 14, 9],
    }
    target6 = {
        "Label": "Label 5"
    }

    # Format data
    views = [view1, view2, view3, view4, view5, view6]
    targets = [target1, target2, target3, target4, target5, target6]

    do = DataObject([None] * len(views), views=views, targets=targets)

    # Plot data
    viz.plot_joint(do, "A", "Label", "A", show=False, calculate_pca=False)
    plt.xlabel("x")
    plt.ylabel("y")
    fp = "images/tests/joint.png"
    dirs, _ = os.path.split(fp)
    if not os.path.exists(dirs):
        os.makedirs(dirs)
    plt.savefig(fp)

    # Plot PCA
    viz.plot_joint(do, "B", "Label", "B", "images/tests/pca_joint.png", show=False)

    # Try out another style
    plt.style.use("seaborn")
    viz.plot_joint(do, "B", "Label", "Seaborn B", "images/tests/pca_joint_seaborn.png", show=False)

    # Reset plotting style
    plt.style.use("ggplot")
