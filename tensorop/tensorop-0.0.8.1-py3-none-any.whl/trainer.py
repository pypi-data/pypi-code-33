import torch.nn as nn
import torch
import torch.nn.functional as F
import torch.optim as optim
from torch.optim import lr_scheduler
from tqdm import tqdm_notebook as tqdm
import numpy as np
import os

def fit(num_epochs,train_loader,model,optimizer=None,criterion=None,scheduler=None):
    if not optimizer:
        optimizer = optim.Adam(model.parameters(), lr=0.0005)
        scheduler = lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.1)
    if not criterion:
        criterion = nn.BCEWithLogitsLoss()
    model.train()
    model.cuda()
    for epoch in range(1, num_epochs+1):
        train_loss = []

        for batch_i, (data, target) in tqdm(enumerate(train_loader), total = len(train_loader)):
            data, target = data.cuda(), target.cuda()

            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target.float())*100
            train_loss.append(loss.item())

            loss.backward()
            optimizer.step()
    
        scheduler.step()
    
        print(f'Epoch {epoch}, train loss: {np.mean(train_loss):.4f}')
        #compute_accuracy(model,train_loader)
        
def evaluate(model,test_loader):
    """
    Returns a nd array containing the predicted label
    """
    preds = []
    model = model.eval()
    for (data,target,name) in tqdm(test_loader):
        data = data.cuda()
        output=model(data)
        _,label=torch.max(output[1],0)
        label = label.cpu().detach().numpy()
        preds.append(label)
    return preds 

def save_model(model,fname):
    try:
        os.mkdir('models')
    except:
        pass
    path = Path('models')
    check = os.path.isfile(os.path.join(path,fname+'.pth.tar'))
    
    if check:
        print("This model already exists,do you want to overwrite it [Y/N]?")
        t = input()
        if t=='Y':
            torch.save(model.state_dict(),os.path.join(path,fname+'.pth.tar'))
            print("Model Overwritten")
        else:
            print("Action Revoked")
    else:
        torch.save(model.state_dict(),os.path.join(path,fname+'.pth.tar'))
        print('Model Saved')
        