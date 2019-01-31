from bootstrap.lib.logger import Logger
from ..mlp import MLP
from .fusions import Block
from .fusions import MLB
from .fusions import MFB
from .fusions import MFH
from .fusions import MCB
from .fusions import Mutan
from .fusions import MLBSum
from .fusions import CatMLP

def factory(opt):
    if 'type' in opt and opt['type'] == 'block':
        fusion = Block(opt)
    elif opt['type'] == 'mlb':
        fusion = MLB(opt)
    elif opt['type'] == 'mfb':
        fusion = MFB(opt)
    elif opt['type'] == 'mfh':
        fusion = MFH(opt)
    elif opt['type'] == 'mcb':
        fusion = MCB(opt)
    elif opt['type'] == 'mutan':
        fusion = Mutan(opt)
    elif opt['type'] == 'mlb_sum':
        fusion = MLBSum(opt)
    elif opt['type'] == 'cat_mlp':
        fusion = CatMLP(opt)
    else:
        raise ValueError()

    Logger().log_value('nb_params_fusion', fusion.n_params, should_print=True)

    return fusion
