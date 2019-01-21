import numpy as np

from .model import ModelSummarizer


class Median(ModelSummarizer):
    """
    Median State Summarizer

    """
    def __init__(self):
        super(Median, self).__init__(np_sum_fn=np.median)

