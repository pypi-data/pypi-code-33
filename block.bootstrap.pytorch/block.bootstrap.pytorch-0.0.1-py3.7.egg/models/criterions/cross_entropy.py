import torch.nn as nn

class CrossEntropyLoss(nn.Module):

    def __init__(self):
        super(CrossEntropyLoss, self).__init__()
        self.loss = nn.CrossEntropyLoss()

    def forward(self, net_out, batch):
        out = {}
        if "class_id" in batch: #Easier than an if in the criterion factory
            out['loss'] = self.loss(
                net_out['logits'],
                batch['class_id'].squeeze(1))
        return out
