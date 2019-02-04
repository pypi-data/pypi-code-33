# -*- coding: utf-8 -*-

"""
This class helps to make sense of the scores during validation.
Keeps track of individual label scores.
"""

from typing import Dict
import cv2
import numpy as np
from k_util import Region, core
from k_vision import text, visual, grid

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


class ScoreMetric:
    def __init__(self, id: int):
        self.id: int = id
        self.n_true_positives: int = 0
        self.n_predictions: int = 0
        self.n_ground_truth: int = 0

    @property
    def precision(self):
        return 1 if self.n_predictions == 0 else self.n_true_positives / self.n_predictions

    @property
    def recall(self):
        return 0 if self.n_ground_truth == 0 else self.n_true_positives / self.n_ground_truth

    @property
    def f1_score(self):
        denominator = (self.precision + self.recall)
        return 0 if denominator == 0 else (2 * self.precision * self.recall) / denominator


class ScoreCounter:
    def __init__(self, label_map: Dict[int, str]):
        self.metric_map: Dict[int, ScoreMetric] = {}
        self.label_map: Dict[int, str] = label_map

    def get_metric(self, id: int) -> ScoreMetric:
        if id not in self.metric_map:
            self.metric_map[id] = ScoreMetric(id)
        return self.metric_map[id]

    def add(self, id: int, n_ground_truth=0, n_true_positives: int=0, n_predictions: int=0):
        metric = self.get_metric(id)
        metric.n_true_positives += n_true_positives
        metric.n_predictions += n_predictions
        metric.n_ground_truth += n_ground_truth

    def get_metrics(self) -> dict:
        """ Returns a dictionary data object with the detailed scores. """
        data = {}
        for m_id, metric in self.metric_map.items():
            metric_data = {
                "id": m_id,
                "label": self.label_map[m_id] if m_id in self.label_map else None,
                "precision": metric.precision,
                "recall": metric.recall,
                "f1": metric.f1_score
            }
            data[m_id] = metric_data
        return data

    def get_f1_score(self):
        """ Get the average F1 score over all classes."""
        f1_scores = [m.f1_score for _, m in self.metric_map.items()]
        f1_score = np.mean(f1_scores)
        return f1_score

    def render(self, path: str, max_per_row=12, score_type: str="f1"):
        """
        Render the metrics to some path.
        Score type is one of "f1", "recall" or "precision".
        """

        plate_w = 300
        plate_h = 32
        text_w = 100
        bar_h = 4
        bar_pad = 12

        images = []
        bg_color = (50, 50, 50)

        # Bar Status Color
        bar_bg_color = (90, 90, 90)
        red_color = (0, 0, 255)
        yellow_color = (0, 200, 255)
        green_color = (0, 255, 0)

        for k, m in self.metric_map.items():
            metric_image = np.zeros((plate_h, plate_w, 3), dtype=np.uint8)
            metric_image[:, :] = bar_bg_color

            if score_type == "f1":
                value = m.f1_score
            elif score_type == "precision":
                value = m.precision
            elif score_type == "recall":
                value = m.recall
            else:
                raise Exception(f"Score type must be one of (f1, recall, precision). Instead, got: {score_type}")

            bar_color = core.interpolate_color(red_color, yellow_color, (value * 2)) if value < 0.5 else \
                core.interpolate_color(yellow_color, green_color, ((value - 0.5) * 2))

            label = f"Class {k}" if k not in self.label_map else self.label_map[k]
            text_region = Region(0, text_w, 0, plate_h)
            metric_image = text.write_into_region(
                metric_image, label.upper(), text_region, h_align=text.ALIGN_RIGHT, font_size=14, bg_color=bg_color)
            visual.draw_bar(metric_image, value, text_w + bar_pad, (plate_h - bar_h) // 2,
                            width=plate_w-text_w-bar_pad * 2, height=bar_h, bar_color=bar_color)
            images.append(metric_image)

        n_col = 1
        while len(images) // n_col > max_per_row:
            n_col += 1

        final_image = grid(images, n_columns=n_col, bg_color=0, inner_y_pad=0)

        title_height = 32
        g_size = final_image.shape
        canvas = np.zeros((g_size[0] + title_height, g_size[1], 3), dtype=np.uint8)
        canvas = text.write_into_region(canvas, f"{score_type} Score".upper(), Region(0, g_size[1], 0, title_height))
        canvas[title_height:title_height + g_size[0], :] = final_image

        if path is not None:
            cv2.imwrite(path, canvas)

        return canvas
