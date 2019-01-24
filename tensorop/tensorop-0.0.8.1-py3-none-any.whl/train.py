import torch

def fit_from_arr(model,criterion,x_train,y_train,split_num,scheduler,permute=True)
"""
Works when you want torch tensors to act as dataloaders
"""
    for i,j in zip(x_train.split(split_num),y_train.split(split_num)):
            if permute: i = i.permute(0,2,1,3)
            cnt+=1
            y_pred = model(i.float())
            loss = criterion(y_pred,j.long())
    
            optimizer.zero_grad()
            loss.backward()
            scheduler.batch_step()
            print(cnt,loss.item()) 
    