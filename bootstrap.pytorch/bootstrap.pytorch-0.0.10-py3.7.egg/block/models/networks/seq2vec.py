import torch
import torch.nn as nn
import torch.nn.functional as F
import skipthoughts
from collections import OrderedDict
from torch.autograd import Variable
from bootstrap.lib.logger import Logger
from bootstrap.lib.options import Options
from skipthoughts import BayesianGRU
from skipthoughts import AbstractUniSkip

def process_lengths(input):
    max_length = input.size(1)
    lengths = list(max_length - input.data.eq(0).sum(1).squeeze())
    return lengths

def select_last(x, lengths):
    batch_size = x.size(0)
    seq_length = x.size(1)
    mask = x.data.new().resize_as_(x.data).fill_(0)
    for i in range(batch_size):
        mask[i][lengths[i]-1].fill_(1)
    mask = Variable(mask)
    x = x.mul(mask)
    x = x.sum(1).view(batch_size, x.size(2))
    return x

class LSTM(nn.Module):

    def __init__(self, vocab, emb_size, hidden_size, num_layers, bidirectional):
        super(LSTM, self).__init__()
        self.vocab = vocab
        self.emb_size = emb_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.bidirectional = bidirectional
        self.embedding = nn.Embedding(num_embeddings=len(self.vocab)+1,
                                      embedding_dim=emb_size,
                                      padding_idx=0)
        if Options()['model']['network'].get('gloves',False):
            emb_size += 300
        self.rnn = nn.LSTM(
            input_size=emb_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=bidirectional)

    def forward(self, input, lengths):
        x = self.embedding(input) # seq2seq
        x = nn.utils.rnn.pack_padded_sequence(x, lengths, batch_first=True)
        x, (hn, cn) = self.rnn(x)
        if self.bidirectional:
            bsize = input.size(0)
            hn = hn[torch.cuda.LongTensor([2,3])].view(bsize,-1) 
        else:
            hn = hn[-1]
        #output = select_last(output, lengths)
        return hn


class TwoLSTM(nn.Module):

    def __init__(self, vocab, emb_size, hidden_size):
        super(TwoLSTM, self).__init__()
        self.vocab = vocab
        self.emb_size = emb_size
        self.hidden_size = hidden_size
        self.embedding = nn.Embedding(num_embeddings=len(self.vocab)+1,
                                      embedding_dim=emb_size,
                                      padding_idx=0)
        self.rnn_0 = nn.LSTM(input_size=emb_size, hidden_size=hidden_size, num_layers=1)
        self.rnn_1 = nn.LSTM(input_size=hidden_size, hidden_size=hidden_size, num_layers=1)

    def forward(self, input):
        lengths = process_lengths(input)
        x = self.embedding(input) # seq2seq
        x = getattr(F, 'tanh')(x)
        x_0, hn = self.rnn_0(x)
        vec_0 = select_last(x_0, lengths)

        # x_1 = F.dropout(x_0, p=0.3, training=self.training)
        # print(x_1.size())
        x_1, hn = self.rnn_1(x_0)
        vec_1 = select_last(x_1, lengths)
        
        vec_0 = F.dropout(vec_0, p=0.3, training=self.training)
        vec_1 = F.dropout(vec_1, p=0.3, training=self.training)
        output = torch.cat((vec_0, vec_1), 1)
        return output


class GloveGRU(nn.Module):

    def __init__(self, vocab, path_txt, dropout):
        super(GloveGRU, self).__init__()
        self.vocab = vocab
        self.path_txt = path_txt
        self.dropout = dropout
        # Load parameters
        import torchwordemb
        dictionary, parameters = torchwordemb.load_glove_text(path_txt)
        nb_unknown = 0
        weight = torch.zeros(len(self.vocab)+1, 300) # first dim = zeros -> +1
        for id_weight, word in enumerate(self.vocab):
            if word in dictionary:
                id_params = dictionary[word]
                weight[id_weight+1] = parameters[id_params]
            else:
                Logger()('Warning: word `{}` not in dictionary'.format(word))
                #params = unknown_params
            
        state_dict = OrderedDict({'weight':weight})
        if nb_unknown > 0:
            Logger('Warning: {}/{} words are not in dictionary, thus set UNK'
                  .format(nb_unknown, len(dictionary)))
        self.embedding = nn.Embedding(num_embeddings=len(self.vocab)+1,
                                      embedding_dim=300,
                                      padding_idx=0)
        self.embedding.load_state_dict(state_dict)

        self.rnn = BayesianGRU(300, 512, dropout=self.dropout)

    def _process_lengths(self, input):
        max_length = input.size(1)
        lengths = list(max_length - input.data.eq(0).sum(1).squeeze())
        return lengths

    def _select_last(self, x, lengths):
        batch_size = x.size(0)
        seq_length = x.size(1)
        mask = x.data.new().resize_as_(x.data).fill_(0)
        for i in range(batch_size):
            mask[i][lengths[i]-1].fill_(1)
        mask = Variable(mask)
        x = x.mul(mask)
        x = x.sum(1).view(batch_size, x.size(2))
        return x

    def forward(self, input, lengths=None):
        if lengths is None:
            lengths = self._process_lengths(input)
        max_length = max(lengths)
        x = self.embedding(input)
        x, hn = self.rnn(x, max_length=max_length) # seq2seq
        x = self._select_last(x, lengths)
        return x


class SRU(AbstractUniSkip):

    def __init__(self, dir_st, vocab, hidden_size=2400,
                 num_layers=1, dropout=0., rnn_dropout=0.,
                 use_tanh=1, use_relu=0, bidirectional=False):
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.rnn_dropout = rnn_dropout
        self.use_tanh = use_tanh
        self.use_relu = use_relu
        self.bidirectional = bidirectional
        super(SRU, self).__init__(dir_st, vocab, dropout=dropout)

    def _load_rnn(self):
        self.rnn = sru.SRU(620, self.hidden_size,
            num_layers=self.num_layers,
            dropout=self.dropout,
            rnn_dropout=self.rnn_dropout,
            use_tanh=self.use_tanh,
            use_relu=self.use_relu,
            bidirectional=self.bidirectional
        )
        return self.rnn

    def forward(self, input, lengths=None):
        if lengths is None:
            lengths = self._process_lengths(input)
        x = self.embedding(input)
        x, hn = self.rnn(x) # seq2seq
        if lengths:
            x = self._select_last(x, lengths)
        return x


def factory(vocab_words, opt):
    list_words = [vocab_words[i+1] for i in range(len(vocab_words))]
    if opt['name'] == 'pretrainedmodels':
        from pretrainedmodels.models.txt_embs import factory as pm_factory
        pm_fn = getattr(pm_factory, opt['type'])
        vocab = {w:i+1 for i,w in enumerate(list_words)}

        if opt['type'] in ['uniskip', 'biskip']:
            seq2vec = pm_fn(vocab,
                args_rnn=opt['args_rnn'],
                pretrained_rnn=opt['pretrained_rnn'],
                pack=opt['pack'])
        else:
            seq2vec = pm_fn(vocab, opt['args_rnn'],
                pretrained_emb=opt['pretrained_emb'],
                dim_emb=opt['dim_emb'])
            

    elif opt['name'] == 'skipthoughts':
        st_class = getattr(skipthoughts, opt['type'])
        seq2vec = st_class(opt['dir_st'],
                           list_words,
                           dropout=opt['dropout'],
                           fixed_emb=opt['fixed_emb'])
    
    elif opt['name'] == '2-lstm':
        seq2vec = TwoLSTM(list_words,
                          opt['emb_size'],
                          opt['hidden_size'])
    elif opt['name'] == 'lstm':
        seq2vec = LSTM(list_words,
                       opt['emb_size'],
                       opt['hidden_size'],
                       opt['num_layers'],
                       opt['bidirectional'])
    elif opt['name'] == 'glove':
        seq2vec = GloveGRU(list_words,
                           opt['path_txt'],
                           opt['dropout'])
    elif opt['name'] == 'sru':
        import sru
        seq2vec = SRU(opt['dir_st'],
                      list_words,
                      hidden_size=opt['hidden_size'],
                      num_layers=opt['num_layers'],
                      dropout=opt['dropout'],
                      rnn_dropout=opt['rnn_dropout'],
                      use_tanh=1,
                      use_relu=0,
                      bidirectional=False)
    else:
        raise NotImplementedError
    return seq2vec


if __name__ == '__main__':

    vocab = ['robots', 'are', 'very', 'cool', '<eos>', 'BiDiBu']
    lstm = TwoLSTM(vocab, 300, 1024)

    input = Variable(torch.LongTensor([
        [1,2,3,4,5,0,0],
        [6,1,2,3,3,4,5],
        [6,1,2,3,3,4,5]
    ]))
    output = lstm(input)
