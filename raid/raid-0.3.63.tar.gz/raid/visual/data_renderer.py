# -*- coding: utf-8 -*-

"""
Given a data-set, we will generate
"""

import os
from typing import Dict, List

import cv2
from k_util import pather, Region
from k_vision import visual, text
import numpy as np
from raid.data.interface.i_sample import ISample

from raid import IDataset

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


def render_sample_predictions(
        samples: List[ISample],
        path: str,
        predictions: list,
        gallery: bool=False
):
    """ Given a set of samples, and a set of predictions, render the results. """

    # Samples and predictions must be the same length.
    assert(len(samples) == len(predictions))

    pather.create(path)
    gallery_images = []

    for i, sample in enumerate(samples):

        prediction_image = sample.get_prediction_image(predictions[i])

        if not gallery:
            # Save each image to disk
            image_path = os.path.join(path, f"predicted_sample_{i}.png")
            cv2.imwrite(image_path, prediction_image)
        else:
            gallery_images.append(prediction_image)

    if gallery:
        gallery_grid = visual.grid(gallery_images)
        image_path = os.path.join(path, f"predicted_gallery.png")
        cv2.imwrite(image_path, gallery_grid)


def render_samples_by_label(
        dataset: IDataset,
        path: str,
        max_samples: int=24,
        max_labels: int=100,
        size: tuple=(64, 64)
):
    """
    Given a data-set, render up to n-instances of up to m-labels into the path.
    Assume that the samples have implemented the get_display_image() function.
    """
    labels = list(dataset.label_map.keys())[:max_labels]
    pather.create(path)
    title_height = 32

    for i in labels:

        samples = dataset.get_samples(i, max_samples)
        semantic_label = dataset.get_semantic_label(i).lower()

        if len(samples) == 0:
            continue

        # Generate the image in a nice gallery.
        images = [s.get_display_image() for s in samples]
        grid_image = visual.grid(images, n_columns=8, image_size=size)

        # Create a canvas so we can add a title.
        grid_h, grid_w, _ = grid_image.shape
        canvas = np.zeros((grid_h + title_height, grid_w, 3), dtype=np.uint8)
        canvas = visual.safe_implant(canvas, grid_image, 0, grid_w, title_height, title_height + grid_h)
        canvas = text.write_into_region(canvas, semantic_label, Region(0, grid_w, 0, title_height),
                                        bg_color=(235, 235, 235), color=(50, 50, 50))

        # Write the image to disk.
        render_path = os.path.join(path, f"render_samples_{semantic_label}.png")
        cv2.imwrite(render_path, canvas)


def render_sample_summary(
        dataset: IDataset,
        path: str,
        samples_per_row: int=8,
        max_labels: int=12,
        size: tuple=(64, 64)
):
    """
    Given a data-set, render up to n-instances of up to m-labels into the path.
    Assume that the samples have implemented the get_display_image() function.
    """
    labels = list(dataset.label_map.keys())[:max_labels]
    pather.create(path)
    title_width = 128

    sample_strips: List[(str, np.ndarray)] = []
    for i in labels:

        samples = dataset.get_samples(i, samples_per_row)
        semantic_label = dataset.get_semantic_label(i).lower()

        if len(samples) == 0:
            continue

        # Generate the image in a nice gallery.
        images = [s.get_display_image() for s in samples]
        grid_image = visual.grid(images, n_rows=1, image_size=size, inner_x_pad=2, outer_pad=2)

        # Create a canvas so we can add a title.
        grid_h, grid_w, _ = grid_image.shape
        canvas = np.zeros((grid_h, title_width + grid_w, 3), dtype=np.uint8)
        canvas = visual.safe_implant(canvas, grid_image, title_width, title_width + grid_w, 0, grid_h)
        canvas = text.write_into_region(canvas, semantic_label, Region(0, title_width, 0, grid_h),
                                        bg_color=(235, 235, 235), color=(50, 50, 50), font_size=14)
        sample_strips.append((semantic_label, canvas))

    sample_strips.sort(key=lambda x: x[0])
    final_width = max([i.shape[1] for _, i in sample_strips])
    final_height = sum([i.shape[0] for _, i in sample_strips])
    final_canvas = np.zeros((final_height, final_width, 3), dtype=np.uint8)

    strip_height = final_height // len(sample_strips)

    for i, strip_tuple in enumerate(sample_strips):
        final_canvas = visual.safe_implant(final_canvas, strip_tuple[1], 0,
                                           final_width, strip_height * i, strip_height * (i + 1))

    # Write the image to disk.
    render_path = os.path.join(path, f"render_sample_summary.png")
    cv2.imwrite(render_path, final_canvas)
