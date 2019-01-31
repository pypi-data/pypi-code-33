import torch
import torch.nn as nn
import torch.nn.functional as F
import numbers

class MLP(nn.Module):
    
    def __init__(self, opt):
        super(MLP, self).__init__()
        self.opt = opt
        self.input_dim = self.opt['input_dim']
        if not isinstance(self.input_dim, numbers.Number):
            self.input_dim = eval(self.input_dim)
        # Modules
        self.linears = nn.ModuleList([nn.Linear(self.input_dim, self.opt['dimensions'][0])])
        for din, dout in zip(self.opt['dimensions'][:-1], self.opt['dimensions'][1:]):
            self.linears.append(nn.Linear(din, dout))
    
    def forward(self, x):
        for i,lin in enumerate(self.linears):
            x = lin(x)
            if (i<len(self.linears)-1):
                x = F.__dict__[self.opt['activation']](x)
                if ('dropout' in self.opt):
                    x = F.dropout(x, self.opt['dropout'], training=self.training)
        return x
