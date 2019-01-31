from bootstrap.lib.options import Options
from . import AccuraciesVQA

def factory(engine, mode):
    if Options()['model']['metric']['name'] == "accuracies_vqa":
        metric = None
        if mode == 'train':
            if engine.dataset["train"].split != "trainval":
                metric = AccuraciesVQA(engine,
                                    mode='train',
                                    open_ended=('tdiuc' not in Options()['dataset']['name']),
                                    tdiuc=True,
                                    dir_exp=Options()['exp']['dir'],
                                    dir_vqa=Options()['dataset']['dir'])
        elif mode == "eval":
            metric = AccuraciesVQA(engine,
                mode='eval',
                open_ended=('tdiuc' not in Options()['dataset']['name']),
                tdiuc=('tdiuc' in Options()['dataset']['name'] or Options()['dataset']['eval_split'] != 'test'),
                dir_exp=Options()['exp']['dir'],
                dir_vqa=Options()['dataset']['dir'])
        else:
            raise ValueError
    else:
        raise ValueError
    return metric
