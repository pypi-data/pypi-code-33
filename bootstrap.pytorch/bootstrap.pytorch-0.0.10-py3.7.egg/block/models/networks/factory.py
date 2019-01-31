import sys
import copy
import torch
import torch.nn as nn
from bootstrap.lib.options import Options
from .vqa import VQA

def factory(engine):
    mode = list(engine.dataset.keys())[0]
    if Options()['model']['network']['name'] == 'VQA':
        net = VQA(Options()['model']['network'],
            wid_to_word=engine.dataset[mode].wid_to_word,
            word_to_wid=engine.dataset[mode].word_to_wid,
            aid_to_ans=engine.dataset[mode].aid_to_ans,
            ans_to_aid=engine.dataset[mode].ans_to_aid)
    else:
        raise ValueError
    return net
