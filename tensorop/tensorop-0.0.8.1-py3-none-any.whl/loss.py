from __future__ import absolute_import
import sys

import torch
from torch import nn

USE_CUDA = torch.cuda.is_available()
device = torch.device("cuda" if USE_CUDA else "cpu")


class TripletLoss(nn.Module):
    def __init__(self,margin=0.3):
        super(TripletLoss,self).__init__()
        self.margin = margin
        self.ranking_loss = nn.MarginRankingLoss(margin=margin)

    def forward(self,inputs,targets):
        """
        targets = ground truth with labels
        """
        n = inputs.size(0)
        #n = len(inputs)
        dist = torch.pow(inputs,2).sum(dim=1,keepdim=True).expand(n,n)
        dist = dist+dist.t()
        dist.addmm_(1,-2,inputs,inputs.t())
        dist = dist.clamp(min=1e-12).sqrt()
        mask = targets.expand(n,n).eq(targets.expand(n,n).t())
        dist_ap,dist_an = [],[]
        for i in range(n):
            dist_ap.append(dist[i][mask[i]].max().unsqueeze(0))
            dist_an.append(dist[i][mask[i]==0].min().unsqueeze(0))
        dist_ap = torch.cat(dist_ap)
        dist_an = torch.cat(dist_an)
        y = torch.ones_like(dist_an)
        loss = self.ranking_loss(dist_an,dist_ap,y)
        return loss

class ConfidentMSELoss(nn.Module):
    def __init__(self,threshold=0.96):
        self.threshold = threshold
        super().__init__()

    def forward(self,input,targets):
        n = input.size(0)
        conf_mask = torch.gt(target,self.threshold).float()
        input_flat = input.view(n,-1)
        target_flat = target.view(n,-1)
        conf_mask_flat = conf_mask.view(n,-1)
        diff = (input_flat-target_flat)**2
        diff_conf = diff*conf_mask_flat
        loss = diff_conf.mean()
        return loss

class FocalLoss(BCE_Loss):
    def weight(self,x,t):
        alpha,gamma=0.25,1
        p = x.sigmoid()
        pt = p*t+(1-p)*(1-t)
        w = alpha*t + (1-alpha)*(1-t)
        return w*(1-pt).pow(gamma)


