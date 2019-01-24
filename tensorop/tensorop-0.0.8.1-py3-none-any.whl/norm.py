import torch
import torch.nn as nn

class LayerNorm(nn.Module):
    """
    LayerNorm(x+Sublayer(x)) 
    SubLayer is the function implemented by sub layer itself
    """
    def __init__(self,features,eps=1e-6):
        super(LayerNorm,self).__init__()
        x = torch.ones(features)
        y = torch.zeros(features)
        self.a = nn.Parameter(x)
        self.b = nn.Parameter(y)
        self.eps = eps
    
    def forward(self,x):
        mean = x.mean(-1,keepdim=True)
        std = x.std(-1,keepdim=True)
        return self.a*(x-mean)/(std+self.eps)+self.b