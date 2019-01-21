import numpy as np

from .model import ModelSummarizer


class Mean(ModelSummarizer):
    """
    Mean State Summarizer

    """
    def __init__(self):
        super(Mean, self).__init__(np_sum_fn=np.mean)
