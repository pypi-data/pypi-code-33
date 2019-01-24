from torch.utils.data import Dataset,DataLoader
from PIL import Image
import numpy as np
import os
import pandas as pd


def get_dataloader(train_loader,test_loader,batch_size,num_workers=4,pin_memory=True):
    train_dl = DataLoader(train_loader, batch_size=batch_size, num_workers=num_workers, pin_memory=True, shuffle=True)
    test_dl = DataLoader(test_loader, batch_size=batch_size, num_workers=num_workers, pin_memory=True)
    return train_dl,test_dl

class ImageDataset_from_csv(Dataset):
    """
    image_folder = dir of image folder (test/train/valid)
    process = 'train/test'
    df: pandas dataframe
    transforms: transformations
    y: labels from LabelEncoder() To get y, use prepare_labels(df[IDs of images])
    num_classes = Num classes
    """
    def __init__(self, image_folder,num_classes,process='train',df=None, transforms=None, y=None):
        self.image_folder = image_folder
        self.imgs_list = [img for img in os.listdir(image_folder)]
        self.process = process
        self.transforms = transforms
        self.num_classes = num_classes
        self.y = y
        if self.process == 'train':
            self.df = df.values
    
    def __len__(self):
        return len(self.imgs_list)-1
    
    def __getitem__(self, idx):
        if self.process == 'train':
            img_name = os.path.join(self.image_folder, self.df[idx][0])
            label = self.y[idx]
        
        elif self.process == 'test':
            img_name = os.path.join(self.image_folder, self.imgs_list[idx])
            label = np.zeros((self.num_classes,))
        
        img = Image.open(img_name).convert('RGB')
        img = self.transforms(img)
        if self.process == 'train':
            return img, label
        elif self.process == 'test':
            return img, label, self.imgs_list[idx]

