from bootstrap.models.model import DefaultModel
from .criterions.cross_entropy import CrossEntropyLoss
from .criterions.kl_divergence import KLDivLoss
from . import networks
from bootstrap.lib.options import Options
from .metrics.accuracies_vqa import AccuraciesVQA

class VQA(DefaultModel):

    def __init__(self, engine=None):
        super(VQA, self).__init__(engine)

    def _init_network(self, engine=None):
        net = networks.VQA(Options()['model']['network'],
                            wid_to_word=engine.dataset[mode].wid_to_word,
                            word_to_wid=engine.dataset[mode].word_to_wid,
                            aid_to_ans=engine.dataset[mode].aid_to_ans,
                            ans_to_aid=engine.dataset[mode].ans_to_aid,
                            vocab_attr=vocab_attr,
                            vocab_obj=vocab_obj,
                            vocab_rel=vocab_rel)
        return net

    def _init_criterions(self, engine=None):
        c = {}
        if 'criterion' in Options()['model'] and \
           'name' in Options()['model']['criterion'] and \
           Options()['model']['criterion']['name'] == 'KLDivLoss':

            if engine and 'train' in engine.dataset:
                c['train'] = KLDivLoss(engine=engine)
            if engine and 'eval' in engine.dataset:
                if 'test' not in engine.dataset['eval'].split:
                    c['eval'] = KLDivLoss()
        else:
            if engine and 'train' in engine.dataset:
                c['train'] = CrossEntropyLoss()
            if engine and 'eval' in engine.dataset:
                if 'test' not in engine.dataset['eval'].split:
                    c['eval'] = CrossEntropyLoss()
        return c

    def _init_metrics(self, engine=None):
        m = {}
        if engine and 'train' in engine.dataset and engine.dataset['train'].split != 'trainval':
            m['train'] = AccuraciesVQA(engine,
                mode='train',
                open_ended=('tdiuc' not in Options()['dataset']['name']),
                tdiuc=True,
                dir_exp=Options()['exp']['dir'],
                dir_vqa=Options()['dataset']['dir'])
        if engine and 'eval' in engine.dataset:
            m['eval'] = AccuraciesVQA(engine,
                mode='eval',
                open_ended=('tdiuc' not in Options()['dataset']['name']),
                tdiuc=('tdiuc' in Options()['dataset']['name'] or Options()['dataset']['eval_split'] != 'test'),
                dir_exp=Options()['exp']['dir'],
                dir_vqa=Options()['dataset']['dir'])
        return m

def factory(engine=None):
    return VQA(engine=engine)
