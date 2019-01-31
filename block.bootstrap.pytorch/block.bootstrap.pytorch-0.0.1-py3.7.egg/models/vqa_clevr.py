from bootstrap.models.model import DefaultModel
from .criterions.cross_entropy import CrossEntropyLoss
#from .networks import VQA as VQANetwork
from bootstrap.lib.options import Options
from .metrics.accuracies_vqa import AccuraciesVQA

class VQAClevr(DefaultModel):

    def __init__(self, engine=None):
        super(VQAClevr, self).__init__(engine)

    # def _init_network(self, engine=None):
    #     mode = list(engine.dataset.keys())[0]
    #     vocab_size = len(engine.dataset[mode].vocab_words())
    #     network = networks.VQA(vocab_size=vocab_size)
    #     return network

    def _init_criterions(self, engine=None):
        c = {}
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
                open_ended=False,
                tdiuc=False)
        if engine and 'eval' in engine.dataset:
            m['eval'] = AccuraciesVQA(engine,
                mode='eval',
                open_ended=False,
                tdiuc=False)
        return m

def factory(engine=None):
    return VQAClevr(engine=engine)