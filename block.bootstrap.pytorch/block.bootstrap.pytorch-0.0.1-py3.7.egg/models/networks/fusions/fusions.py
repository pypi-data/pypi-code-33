import torch
import torch.nn as nn
import torch.nn.functional as F
from .compactbilinearpooling import CompactBilinearPooling

def _get_sizes_list(dim, chunks):
    split_size = (dim + chunks - 1) // chunks
    sizes_list = [split_size] * chunks
    sizes_list[-1] = sizes_list[-1] - (sum(sizes_list) - dim) # Adjust last
    assert sum(sizes_list) == dim
    if sizes_list[-1]<0:
        n_miss = sizes_list[-2] - sizes_list[-1]
        sizes_list[-1] = sizes_list[-2]
        for j in range(n_miss):
            sizes_list[-j-1] -= 1
        assert sum(sizes_list) == dim
        assert min(sizes_list) > 0
    return sizes_list

def _get_chunks(x,sizes):
    out = []
    begin = 0
    for s in sizes:
        y = x.narrow(1,begin,s)
        out.append(y)
        begin += s
    return out


class Block(nn.Module):

    def __init__(self, opt):
        super(Block, self).__init__()
        self.opt = opt
        if 'use_embeddings' in self.opt and self.opt['use_embeddings']:
            self.linear0 = nn.Embedding(self.opt['input_dims'][0],
                                        self.opt['mutan_dim'])
        else:
            self.linear0 = nn.Linear(self.opt['input_dims'][0],
                                     self.opt['mutan_dim'])
        if self.opt['shared']:
            self.linear1 = self.linear0
        else:
            if 'use_embeddings' in self.opt and self.opt['use_embeddings']:
                self.linear1 = nn.Embedding(self.opt['input_dims'][1],
                                            self.opt['mutan_dim'])
            else:
                self.linear1 = nn.Linear(self.opt['input_dims'][1],
                                         self.opt['mutan_dim'])

        self.sizes_list = _get_sizes_list(self.opt['mutan_dim'], self.opt['chunks'])
        merge_linears0, merge_linears1 = [], []
        for size in self.sizes_list:
            ml0 = nn.Linear(size, size*self.opt['rank'])
            merge_linears0.append(
                ml0
            )
            if self.opt['shared']:
                ml1 = ml0
            else:
                ml1 = nn.Linear(size, size*self.opt['rank'])
            merge_linears1.append(
                ml1
            )
        self.merge_linears0 = nn.ModuleList(merge_linears0)
        self.merge_linears1 = nn.ModuleList(merge_linears1)

        self.linear_out = nn.Linear(self.opt['mutan_dim'], self.opt['output_dim'])

        self.n_params = sum(p.numel() for p in self.parameters() if p.requires_grad)
        self.hidden = None

    def forward(self, x):
        reshape = False
        if x[0].dim() == 3:
            reshape = True
            original_bsize = x[0].size(0)
            nb_regions = x[0].size(1)
            x[0] = x[0].contiguous().view(original_bsize*nb_regions,-1)
        if x[1].dim() == 3:
            reshape = True
            original_bsize = x[1].size(0)
            nb_regions = x[1].size(1)
            x[1] = x[1].contiguous().view(original_bsize*nb_regions,-1)

        x0 = self.linear0(x[0])
        x1 = self.linear1(x[1])
        bsize = x1.size(0)
        if 'dropout_input' in self.opt:
            x0 = F.dropout(x0, p=self.opt['dropout_input'], training=self.training)
            x1 = F.dropout(x1, p=self.opt['dropout_input'], training=self.training)
        x0_chunks = _get_chunks(x0, self.sizes_list)
        x1_chunks = _get_chunks(x1, self.sizes_list)
        zs = []
        for chunk_id, m0, m1 in zip(range(len(self.sizes_list)),
                                    self.merge_linears0,
                                    self.merge_linears1):
            x0_c = x0_chunks[chunk_id]
            x1_c = x1_chunks[chunk_id]
            m = m0(x0_c) * m1(x1_c) # bsize x split_size*rank
            m = m.view(bsize, self.opt['rank'], -1)
            z = torch.sum(m, 1)
            z = torch.sqrt(F.relu(z)) - torch.sqrt(F.relu(-z))
            z = F.normalize(z,p=2)
            zs.append(z)
        z = torch.cat(zs,1)

        if not reshape:
            self.hidden = z

        if 'dropout_pre_lin' in self.opt:
            z = F.dropout(z, p=self.opt['dropout_pre_lin'], training=self.training)
        z = self.linear_out(z)
        if 'dropout_output' in self.opt:
            z = F.dropout(z, p=self.opt['dropout_output'], training=self.training)

        if reshape:
            z = z.view(original_bsize, nb_regions, -1)

        return z


class Mutan(nn.Module):

    def __init__(self, opt):
        super(Mutan, self).__init__()
        self.opt = opt
        if 'use_embeddings' in self.opt and self.opt['use_embeddings']:
            self.linear0 = nn.Embedding(self.opt['input_dims'][0],
                                        self.opt['mutan_dim'])
        else:
            self.linear0 = nn.Linear(self.opt['input_dims'][0],
                                     self.opt['mutan_dim'])
        self.merge_linear0 = nn.Linear(self.opt['mutan_dim'],
                                       self.opt['mutan_dim']*self.opt['rank'])
        if self.opt['shared']:
            self.linear1 = self.linear0
            self.merge_linear1 = self.merge_linear0
        else:
            if 'use_embeddings' in self.opt and self.opt['use_embeddings']:
                self.linear1 = nn.Embedding(self.opt['input_dims'][1],
                                            self.opt['mutan_dim'])
            else:
                self.linear1 = nn.Linear(self.opt['input_dims'][1],
                                         self.opt['mutan_dim'])
            self.merge_linear1 = nn.Linear(self.opt['mutan_dim'],
                                           self.opt['mutan_dim']*self.opt['rank'])
        self.linear_out = nn.Linear(self.opt['mutan_dim'], self.opt['output_dim'])

        self.n_params = sum(p.numel() for p in self.parameters() if p.requires_grad)

        Logger()('Number of parameters: {}'.format(self.n_params))


    def forward(self, x):
        x0 = self.linear0(x[0])
        x1 = self.linear1(x[1])
        if 'dropout_input' in self.opt:
            x0 = F.dropout(x0, p=self.opt['dropout_input'], training=self.training)
            x1 = F.dropout(x1, p=self.opt['dropout_input'], training=self.training)
        m0 = self.merge_linear0(x0)
        m1 = self.merge_linear1(x1)
        m = m0 * m1
        m = m.view(-1, self.opt['rank'], self.opt['mutan_dim'])
        z = torch.sum(m, 1)
        z = torch.sqrt(F.relu(z)) - torch.sqrt(F.relu(-z))
        z = F.normalize(z,p=2)
        if 'dropout_pre_lin' in self.opt:
            z = F.dropout(z, p=self.opt['dropout_pre_lin'], training=self.training)
        z = self.linear_out(z)
        if 'dropout_output' in self.opt:
            z = F.dropout(z, p=self.opt['dropout_output'], training=self.training)
        return z


class MLB(nn.Module):

    def __init__(self, opt):
        super(MLB, self).__init__()
        self.opt = opt
        # Modules
        self.linear0 = nn.Linear(self.opt['input_dims'][0],
                                 self.opt['mlb_dim'])
        self.linear1 = nn.Linear(self.opt['input_dims'][1],
                                 self.opt['mlb_dim'])
        self.linear_out = nn.Linear(self.opt['mlb_dim'],
                                    self.opt['output_dim'])
        self.n_params = sum(p.numel() for p in self.parameters() if p.requires_grad)

        Logger()('Number of parameters: {}'.format(self.n_params))


    def forward(self, x):
        x0 = self.linear0(x[0])
        x1 = self.linear1(x[1])

        if 'activ_input' in self.opt:
            x0 = getattr(F, self.opt['activ_input'])(x0)
            x1 = getattr(F, self.opt['activ_input'])(x1)

        if 'dropout_input' in self.opt:
            x0 = F.dropout(x0, p=self.opt['dropout_input'], training=self.training)
            x1 = F.dropout(x1, p=self.opt['dropout_input'], training=self.training)

        z = x0 * x1

        if 'normalize' in self.opt and self.opt['normalize']:
            z = torch.sqrt(F.relu(z)) - torch.sqrt(F.relu(-z))
            z = F.normalize(z,p=2)

        if 'dropout_pre_lin' in self.opt:
            z = F.dropout(z, p=self.opt['dropout_pre_lin'], training=self.training)

        z = self.linear_out(z)

        if 'activ_output' in self.opt:
            z = getattr(F, self.opt['activ_output'])(z)

        if 'dropout_output' in self.opt:
            z = F.dropout(z, p=self.opt['dropout_output'], training=self.training)
        return z


class MFB(nn.Module):

    def __init__(self, opt):
        super(MFB, self).__init__()
        self.opt = opt
        # Modules
        self.linear0 = nn.Linear(self.opt['input_dims'][0],
                                 self.opt['mfb_dim']*self.opt['mfb_factor'])
        self.linear1 = nn.Linear(self.opt['input_dims'][1],
                                 self.opt['mfb_dim']*self.opt['mfb_factor'])
        self.linear_out = nn.Linear(self.opt['mfb_dim'],
                                    self.opt['output_dim'])

        self.n_params = sum(p.numel() for p in self.parameters() if p.requires_grad)

        Logger()('Number of parameters: {}'.format(self.n_params))

    def forward(self, x):
        reshape = False
        if x[0].dim() == 3:
            reshape = True
            original_bsize = x[0].size(0)
            nb_regions = x[0].size(1)
            x[0] = x[0].contiguous().view(original_bsize*nb_regions,-1)
        if x[1].dim() == 3:
            reshape = True
            original_bsize = x[1].size(0)
            nb_regions = x[1].size(1)
            x[1] = x[1].contiguous().view(original_bsize*nb_regions,-1)

        x0 = self.linear0(x[0])
        x1 = self.linear1(x[1])

        if 'activ_input' in self.opt:
            x0 = getattr(F, self.opt['activ_input'])(x0)
            x1 = getattr(F, self.opt['activ_input'])(x1)

        if 'dropout_input' in self.opt:
            x0 = F.dropout(x0, p=self.opt['dropout_input'], training=self.training)
            x1 = F.dropout(x1, p=self.opt['dropout_input'], training=self.training)

        z = x0 * x1

        if 'dropout_pre_norm' in self.opt:
            z = F.dropout(z, p=self.opt['dropout_pre_norm'], training=self.training)

        z = z.view(z.size(0), self.opt['mfb_dim'], self.opt['mfb_factor'])
        z = z.sum(2)

        if 'normalize' in self.opt and self.opt['normalize']:
            z = torch.sqrt(F.relu(z)) - torch.sqrt(F.relu(-z))
            z = F.normalize(z,p=2)

        z = self.linear_out(z)

        if 'activ_output' in self.opt:
            z = getattr(F, self.opt['activ_output'])(z)

        if 'dropout_output' in self.opt:
            z = F.dropout(z, p=self.opt['dropout_output'], training=self.training)

        if reshape:
            z = z.view(original_bsize, nb_regions, -1)
        return z


class MFH(nn.Module):

    def __init__(self, opt):
        super(MFH, self).__init__()
        self.opt = opt
        # Modules
        self.linear0_0 = nn.Linear(self.opt['input_dims'][0],
                                 self.opt['mfh_dim']*self.opt['mfh_factor'])
        self.linear1_0 = nn.Linear(self.opt['input_dims'][1],
                                 self.opt['mfh_dim']*self.opt['mfh_factor'])

        self.linear0_1 = nn.Linear(self.opt['input_dims'][0],
                                 self.opt['mfh_dim']*self.opt['mfh_factor'])
        self.linear1_1 = nn.Linear(self.opt['input_dims'][1],
                                 self.opt['mfh_dim']*self.opt['mfh_factor'])

        self.linear_out = nn.Linear(self.opt['mfh_dim']*2,
                                    self.opt['output_dim'])

        self.n_params = sum(p.numel() for p in self.parameters() if p.requires_grad)

        Logger()('Number of parameters: {}'.format(self.n_params))

    def forward(self, x):
        reshape = False
        if x[0].dim() == 3:
            reshape = True
            original_bsize = x[0].size(0)
            nb_regions = x[0].size(1)
            x[0] = x[0].contiguous().view(original_bsize*nb_regions,-1)
        if x[1].dim() == 3:
            reshape = True
            original_bsize = x[1].size(0)
            nb_regions = x[1].size(1)
            x[1] = x[1].contiguous().view(original_bsize*nb_regions,-1)

        x0 = self.linear0_0(x[0])
        x1 = self.linear1_0(x[1])

        if 'activ_input' in self.opt:
            x0 = getattr(F, self.opt['activ_input'])(x0)
            x1 = getattr(F, self.opt['activ_input'])(x1)

        if 'dropout_input' in self.opt:
            x0 = F.dropout(x0, p=self.opt['dropout_input'], training=self.training)
            x1 = F.dropout(x1, p=self.opt['dropout_input'], training=self.training)

        z_0_skip = x0 * x1

        if 'dropout_pre_lin' in self.opt:
            z_0_skip = F.dropout(z_0_skip, p=self.opt['dropout_pre_lin'], training=self.training)

        z_0 = z_0_skip.view(z_0_skip.size(0), self.opt['mfh_dim'], self.opt['mfh_factor'])
        z_0 = z_0.sum(2)

        if 'normalize' in self.opt and self.opt['normalize']:
            z_0 = torch.sqrt(F.relu(z_0)) - torch.sqrt(F.relu(-z_0))
            z_0 = F.normalize(z_0, p=2)

        #
        x0 = self.linear0_1(x[0])
        x1 = self.linear1_1(x[1])

        if 'activ_input' in self.opt:
            x0 = getattr(F, self.opt['activ_input'])(x0)
            x1 = getattr(F, self.opt['activ_input'])(x1)

        if 'dropout_input' in self.opt:
            x0 = F.dropout(x0, p=self.opt['dropout_input'], training=self.training)
            x1 = F.dropout(x1, p=self.opt['dropout_input'], training=self.training)

        z_1 = x0 * x1 * z_0_skip

        if 'dropout_pre_lin' in self.opt:
            z_1 = F.dropout(z_1, p=self.opt['dropout_pre_lin'], training=self.training)

        z_1 = z_1.view(z_1.size(0), self.opt['mfh_dim'], self.opt['mfh_factor'])
        z_1 = z_1.sum(2)

        if 'normalize' in self.opt and self.opt['normalize']:
            z_1 = torch.sqrt(F.relu(z_1)) - torch.sqrt(F.relu(-z_1))
            z_1 = F.normalize(z_1, p=2)

        #
        cat_dim = z_0.dim() - 1
        z = torch.cat([z_0, z_1], cat_dim)
        z = self.linear_out(z)

        if 'activ_output' in self.opt:
            z = getattr(F, self.opt['activ_output'])(z)

        if 'dropout_output' in self.opt:
            z = F.dropout(z, p=self.opt['dropout_output'], training=self.training)

        if reshape:
            z = z.view(original_bsize, nb_regions, -1)

        return z


class MCB(nn.Module):

    def __init__(self, opt):
        super(MCB, self).__init__()
        self.opt = opt
        # Modules
        self.mcb = CompactBilinearPooling(
            self.opt['input_dims'][0],
            self.opt['input_dims'][1],
            self.opt['mcb_dim'])

        self.linear_out = nn.Linear(self.opt['mcb_dim'],
                                    self.opt['output_dim'])

        Logger()('Number of parameters: {}'.format(
            sum(p.numel() for p in self.parameters() if p.requires_grad)))

    def forward(self, x):
        z = self.mcb(x[0], x[1])

        z = self.linear_out(z)

        if 'activ_output' in self.opt:
            z = getattr(F, self.opt['activ_output'])(z)

        if 'dropout_output' in self.opt:
            z = F.dropout(z, p=self.opt['dropout_output'], training=self.training)
        return z


class MLBSum(nn.Module):

    def __init__(self, opt):
        super(MLBSum, self).__init__()
        self.opt = opt
        # Modules
        self.linear0 = nn.Linear(self.opt['input_dims'][0],
                                 self.opt['mlb_dim'])
        self.linear1 = nn.Linear(self.opt['input_dims'][1],
                                 self.opt['mlb_dim'])
        self.linear_out = nn.Linear(self.opt['mlb_dim'],
                                    self.opt['output_dim'])

        Logger()('Number of parameters: {}'.format(
            sum(p.numel() for p in self.parameters() if p.requires_grad)))


    def forward(self, x):
        x0 = self.linear0(x[0])
        x1 = self.linear1(x[1])

        if 'activ_input' in self.opt:
            x0 = getattr(F, self.opt['activ_input'])(x0)
            x1 = getattr(F, self.opt['activ_input'])(x1)

        if 'dropout_input' in self.opt:
            x0 = F.dropout(x0, p=self.opt['dropout_input'], training=self.training)
            x1 = F.dropout(x1, p=self.opt['dropout_input'], training=self.training)

        z = x0 + x1

        if 'normalize' in self.opt and self.opt['normalize']:
            z = torch.sqrt(F.relu(z)) - torch.sqrt(F.relu(-z))
            z = F.normalize(z,p=2)

        if 'dropout_pre_lin' in self.opt:
            z = F.dropout(z, p=self.opt['dropout_pre_lin'], training=self.training)

        z = self.linear_out(z)

        if 'activ_output' in self.opt:
            z = getattr(F, self.opt['activ_output'])(z)

        if 'dropout_output' in self.opt:
            z = F.dropout(z, p=self.opt['dropout_output'], training=self.training)
        return z


class CatMLP(nn.Module):

    def __init__(self, opt):
        super(CatMLP, self).__init__()
        self.opt = copy.copy(opt)
        self.opt['input_dim'] = sum(self.opt['input_dims'])
        self.opt['dimensions'].append(self.opt['output_dim'])
        # Modules
        self.mlp = MLP(self.opt)

        Logger()('Number of parameters: {}'.format(
            sum(p.numel() for p in self.parameters() if p.requires_grad)))

    def forward(self, x):
        if x[0].dim() == 3 and x[1].dim() == 2:
            x[1] = x[1].unsqueeze(1).reshape_as(x[0])
        if x[1].dim() == 3 and x[0].dim() == 2:
            x[0] = x[0].unsqueeze(1).reshape_as(x[1])
        z = torch.cat(x, dim=x[0].dim()-1)
        z = self.mlp(z)
        return z

class Tucker(nn.Module):

    def __init__(self, opt):
        super(Tucker, self).__init__()
        self.opt = opt

        self.linear0 = nn.Linear(self.opt['input_dims'][0],
                                 self.opt['tucker_dim'])

        self.linear1 = nn.Linear(self.opt['input_dims'][1],
                                 self.opt['tucker_dim'])

        self.bilinear = nn.Bilinear(
            self.opt['tucker_dim'],
            self.opt['tucker_dim'],
            self.opt['tucker_dim'])

        self.linear_out = nn.Linear(self.opt['tucker_dim'], self.opt['output_dim'])

        Logger()('Number of parameters: {}'.format(
            sum(p.numel() for p in self.parameters() if p.requires_grad)))

    def forward(self, x):
        reshape = False
        if x[0].dim() == 3:
            reshape = True
            original_bsize = x[0].size(0)
            nb_regions = x[0].size(1)
            x[0] = x[0].contiguous().view(original_bsize*nb_regions,-1)
        if x[1].dim() == 3:
            reshape = True
            original_bsize = x[1].size(0)
            nb_regions = x[1].size(1)
            x[1] = x[1].contiguous().view(original_bsize*nb_regions,-1)

        x0 = self.linear0(x[0])
        x1 = self.linear1(x[1])

        if 'dropout_input' in self.opt:
            x0 = F.dropout(x0, p=self.opt['dropout_input'], training=self.training)
            x1 = F.dropout(x1, p=self.opt['dropout_input'], training=self.training)

        z = self.bilinear(x0, x1)

        if self.opt.get('normalize', False):
            z = torch.sqrt(F.relu(z)) - torch.sqrt(F.relu(-z))
            z = F.normalize(z,p=2)

        if 'dropout_pre_lin' in self.opt:
            z = F.dropout(z, p=self.opt['dropout_pre_lin'], training=self.training)

        z = self.linear_out(z)

        if 'dropout_output' in self.opt:
            z = F.dropout(z, p=self.opt['dropout_output'], training=self.training)

        if reshape:
            z = z.view(original_bsize, nb_regions, -1)

        return z
