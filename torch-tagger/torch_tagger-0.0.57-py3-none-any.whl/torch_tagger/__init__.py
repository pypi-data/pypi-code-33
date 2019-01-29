"""NLP Tagger Tools built by pyTorch

.. moduleauthor:: Infinity Future <infinityfuture@foxmaill>

"""

from .tagger import Tagger
from .torch_lm import START_TAG, STOP_TAG, PAD_TAG, UNK_TAG

__all__ = ['Tagger', 'START_TAG', 'STOP_TAG', 'PAD_TAG', 'UNK_TAG']
