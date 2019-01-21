from collections import OrderedDict, deque

import numpy as np
import torch

from tatau.nn.tatau.summarizer.summarizer import Summarizer


class WeightsSummarizer(Summarizer):
    def __init__(self, np_sum_fn):
        super(WeightsSummarizer, self).__init__()
        self._np_sum_fn = np_sum_fn

    def summarize(self, updates):
        state_dict_all = OrderedDict()
        for state_dict in updates:
            for key, value in state_dict.items():
                if torch.is_tensor(value):
                    if key not in state_dict_all:
                        state_dict_all[key] = deque()
                    state_dict_all[key].append(value.detach().cpu().numpy())

        new_state_dict = OrderedDict()
        for key, arr in state_dict_all.items():
            array = np.array(arr)
            sum_array = self._np_sum_fn(array, axis=0)
            # pylint: disable=E1102
            new_state_dict[key] = torch.tensor(data=sum_array)

        return new_state_dict
