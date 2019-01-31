# -*- coding: utf-8 -*-

"""
A special case of the multi-label classification where there is only one label.
"""

from typing import Dict
from raid.data.interface.i_sample import ISample

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


class ISingleClfSample(ISample):
    def __init__(self, id: str, label: int, label_map: Dict[int, str]):
        super().__init__(id, [label], label_map)

    @property
    def semantic_label(self):
        return self.semantic_labels[0]

    @property
    def label(self) -> int:
        return self.labels[0]
