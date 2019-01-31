import torch.nn as nn
import torch.nn.functional as F
from . import fusion

class AbstractNoAtt(nn.Module):

    def __init__(self, opt={},
            vocab_words=[], vocab_answers=[],
            img_enc=None, txt_enc=None):
        super(AbstractNoAtt, self).__init__()
        self.opt = opt
        self.vocab_words = vocab_words
        self.vocab_answers = vocab_answers
        self.num_classes = len(self.vocab_answers)
        # Modules
        self.img_enc = img_enc
        self.txt_enc = txt_enc
        self.linear_classif = nn.Linear(self.opt['fusion']['dim_h'], self.num_classes)

    def _fusion(self, input_v, input_q):
        raise NotImplementedError

    def _classif(self, x):
        if 'activation' in self.opt['classif']:
            x = getattr(F, self.opt['classif']['activation'])(x)
        x = F.dropout(x, p=self.opt['classif']['dropout'], training=self.training)
        x = self.linear_classif(x)
        return x

    def forward(self, batch):
        batch_size = batch['visual'].size(0)
        if self.img_enc is not None:
            x_v = self.img_enc.features(batch['visual'])
            x_v = x_v.sum(3).sum(2).view(batch_size, -1)
        else:
            x_v = batch['visual']
        if self.txt_enc is not None:
            x_q = self.txt_enc(batch['question'])
        else:
            x_q = batch['question']
        x = self._fusion(x_v, x_q)
        x = self._classif(x)

        _, pred = x.data.max(1)
        pred.squeeze_()
        out = {}
        out['logits'] = x
        out['answer_ids'] = []
        out['answers'] = []
        for i in range(batch_size):
            out['answers'].append(self.vocab_answers[pred[i]])
            out['answer_ids'].append(pred[i])
        return out


class MLBNoAtt(AbstractNoAtt):

    def __init__(self, opt={},
            vocab_words=[], vocab_answers=[],
            img_enc=None, txt_enc=None):
        super(MLBNoAtt, self).__init__(opt, vocab_words, vocab_answers, img_enc, txt_enc)
        self.fusion = fusion.MLBFusion(self.opt['fusion'])

    def _fusion(self, input_v, input_q):
        x = self.fusion(input_v, input_q)
        return x


class MutanNoAtt(AbstractNoAtt):

    def __init__(self, opt={},
                 vocab_words=[],
                 vocab_answers=[],
                 img_enc=None, txt_enc=None):
        opt['fusion']['dim_h'] = opt['fusion']['dim_mm']
        super(MutanNoAtt, self).__init__(opt, vocab_words, vocab_answers, img_enc, txt_enc)
        self.fusion = fusion.MutanFusion(self.opt['fusion'])

    def _fusion(self, input_v, input_q):
        x = self.fusion(input_v, input_q)
        return x
