import torch
import numpy as np
from torch import nn
from torch.autograd import Variable

if torch.cuda.is_available():
    default_device = torch.device('cuda')
else:
    default_device = torch.device('cpu')

def add_padding(t,n,c,h,w,pad_value,axis):
    padding = Variable(torch.zeros(n,pad_value,h,w))
    padded_inp = torch.cat((t,padding),axis)
    padded_inp = padded_inp.float()
    return padded_inp

def torch2np(t):
    return t.numpy()

def np2torch(t):
    return torch.from_numpy(t)

def list2torch(t,type='float'):
    k = torch.FloatTensor(t)
    if type=='long':   k = k.long()
    return k

def Flatten(input):
    """
    Takes a Torch Tensor or Numpy array and Flattens it out giving a single dimensional tensor
    """
    try:
	    return input.flatten()
    except:
	    return input.view(-1)

activation = {}
"""
model.conv.register_forward_hook(get_activation('attr'))
"""
def get_activation(name):
    def hook(model,input,output):
        activation[name] = output.detach()
    return hook

def load_model(model,file):
    """
    Input:
        Model: h5py file which contains model's weights
        file: Path to file
    Output:
        Model: Saved Model
        start_epoch: Mark of epoch
    """
    checkpoint = torch.load(file)
    model.load_state_dict(checkpoint['state_dict'])
    start_epoch = checkpoint['epoch']
    print("Model size: {:.5f}M".format(sum(p.numel() for p in model.parameters())/1000000.0))
    return start_epoch,model
