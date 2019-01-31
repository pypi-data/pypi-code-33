import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from block.models.networks.seq2vec import factory as factory_seq2vec
from bootstrap.datasets import transforms as bootstrap_tf
from bootstrap.lib.options import Options
from .fusions.factory import factory as factory_fusion

def mask_softmax(input, lengths):#, dim=1)
    mask = torch.zeros_like(input)
    t_lengths = torch.LongTensor(lengths)[:,None, None].expand_as(mask)
    arange_id = torch.arange(mask.size(1))[None,:,None].expand_as(mask)
    if mask.is_cuda:
        t_lengths = t_lengths.cuda()
        arange_id = arange_id.cuda()
    mask[arange_id<t_lengths] = 1
    input = torch.exp(input)
    input = input * mask
    input = input / torch.sum(input, dim=1, keepdim=True).expand_as(input)
    return input


class VQA(nn.Module):

    def __init__(self, opt,
            wid_to_word={},
            word_to_wid={},
            aid_to_ans=[],
            ans_to_aid={}):
        super(VQA, self).__init__()
        self.opt = opt
        self.wid_to_word = wid_to_word
        self.word_to_wid = word_to_wid
        self.aid_to_ans = aid_to_ans
        self.ans_to_aid = ans_to_aid

        # Modules
        self.txt_enc = factory_seq2vec(self.wid_to_word, self.opt['txt_enc'])

        if 'classic_attention' in self.opt:
            if 'nb_glimpses' in self.opt['classic_attention']:
                self.classic_glimpse = nn.ModuleList()
                for i in range(self.opt['classic_attention']['nb_glimpses']):
                    self.classic_glimpse.append(ClassicAttention(
                        self.opt['classic_attention']
                    ))
            else:
                self.classic_glimpse = ClassicAttention(
                    self.opt['classic_attention']
                )
        else:
            self.classic_glimpse = None

        if self.opt.get('self_q_att', False):
            if self.opt.get('gloves',False):
                self.q_att_linear0 = nn.Linear(1024, 512)
            else:
                self.q_att_linear0 = nn.Linear(2400, 512)
            self.q_att_linear1 = nn.Linear(512, 2)

        self.fusion = factory_fusion(self.opt['fusion'])
        self.q_att_coeffs = None
        self.q = None
        self.v = None

    def forward(self, batch):
        if type(batch['lengths']) != list:
            batch['lengths'] = list(batch['lengths'].data[:,0]) # ugly hack

        q, wq_r = self._get_question_vectors(
            batch['question'],
            batch['lengths'],
            batch.get('gloves',None))
        self.q = q
        glimpses = []

        if self.classic_glimpse is not None:
            if 'nb_glimpses' in self.opt['classic_attention']:
                for i in range(self.opt['classic_attention']['nb_glimpses']):
                    glimpses.append(
                        self.classic_glimpse[i](q, batch)
                    )
            else:
                glimpses.append(
                    self.classic_glimpse(q, batch)
                )

        if 'aggreg' in self.opt['fusion']:
            if self.opt['fusion']['aggreg'] == 'cat':
                v = torch.cat(glimpses, dim=1)
            elif self.opt['fusion']['aggreg'] == 'sum':
                v = torch.stack(glimpses, dim=1).sum(1)
            else:
                raise ValueError
        else:
            v = torch.cat(glimpses, dim=1)

        self.v = v

        try:
            x = self.fusion([v,q])
        except:
            import ipdb;ipdb.set_trace()

        out = {}
        out['logits'] = x
        return out


    def process_answers(self, out):
        batch_size = out['logits'].shape[0]
        _, pred = out['logits'].data.max(1)
        pred.squeeze_()
        out['answers'] = [self.aid_to_ans[pred[i]] for i in range(batch_size)]
        out['answer_ids'] = [pred[i] for i in range(batch_size)]
        return out

    def _get_question_vectors(self, question, lengths, gloves=None):
        if Options()['model']['network']['txt_enc']['name'] == 'lstmlol':
            q = self.txt_enc(question, lengths)
            return q, None

        wq = self.txt_enc.embedding(question)
        mask_Q = (question!=0).view(-1,question.size(1), 1).expand_as(wq)
        mask_Q = mask_Q.float()
        wq = wq*mask_Q

        if self.opt.get('gloves',False):
            wq = torch.cat([wq, gloves], dim=2)

        q, _ = self.txt_enc.rnn(wq)

        if self.opt.get('self_q_att', False):
            q_att = self.q_att_linear0(q)
            q_att = F.relu(q_att)
            q_att = self.q_att_linear1(q_att)
            q_att = mask_softmax(q_att, lengths)
            self.q_att_coeffs = q_att
            if q_att.size(2) > 1:
                q_atts = torch.unbind(q_att, dim=2)
                q_outs = []
                for q_att in q_atts:
                    q_att = q_att.unsqueeze(2)
                    q_att = q_att.expand_as(q)
                    q_out = q_att*q
                    q_out = q_out.sum(1)
                    q_outs.append(q_out)
                q = torch.cat(q_outs, dim=1)
            else:
                q_att = q_att.expand_as(q)
                q = q_att * q
                q = q.sum(1)
        else:
            q = self.txt_enc._select_last(q, lengths)

        if self.opt.get('gloves',False):
            mask_Q = torch.cat([mask_Q,mask_Q],dim=2)
        wq = torch.sum(wq, 1)
        wq = wq / torch.sum(mask_Q, 1, keepdim=False).float()

        # For now, we only do a global average pooling on word embeddings. But later, we
        # should weight each word according to whether it is object, attribute or relationship
        return q, wq


class ClassicAttention(nn.Module):

    def __init__(self, opt):
        super(ClassicAttention, self).__init__()
        self.opt = opt
        self.fusion = factory_fusion(self.opt)
        if self.opt.get('with_mlp',False):
            self.linear0 = nn.Linear(self.opt['output_dim'],512)
            self.linear1 = nn.Linear(512, self.opt.get('mlp_glimpses',2))
        self.v_att_coeffs = None


    def forward(self, q, batch):
        v_features = batch['pooled_feat']
        alpha = self._attention(q, v_features)

        if self.opt.get('with_mlp',False):
            alpha = self.linear0(alpha)
            alpha = F.relu(alpha)
            alpha = self.linear1(alpha)

        if 'nb_objects' in batch and min(batch['nb_objects']) != max(batch['nb_objects']):
            alpha = mask_softmax(alpha, batch['nb_objects']).expand_as(v_features)
        else:
            alpha = F.softmax(alpha, dim=1)
        self.v_att_coeffs = alpha

        if alpha.size(2) > 1: # nb_glimpses > 1
            alphas = torch.unbind(alpha, dim=2)
            v_outs = []
            for alpha in alphas:
                alpha = alpha.unsqueeze(2).expand_as(v_features)
                v_out = alpha*v_features
                v_out = v_out.sum(1)
                v_outs.append(v_out)
            v_out = torch.cat(v_outs, dim=1)
        else:
            alpha = alpha.expand_as(v_features)
            v_out = alpha*v_features
            v_out = v_out.sum(1)
        return v_out

    def _attention(self, q, v_features):
        batch_size = q.size(0)
        n_regions = v_features.size(1)
        q_fusion = q[:,None,:].expand(q.size(0), n_regions, q.size(1))
        out = self.fusion([
            q_fusion.contiguous().view(batch_size*n_regions, -1),
            v_features.contiguous().view(batch_size*n_regions, -1)
        ])
        out = out.view(batch_size, n_regions, -1)
        return out
