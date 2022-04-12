import torch
import imageio
import os
from torch.utils.data import Dataset


class DemonstrationImageDataset(Dataset):
    def __init__(self,img_dir_true,img_dir_false):
        self.img_dirs = [os.path.join(img_dir_true,img) for img in os.listdir(img_dir_true) if os.path.isfile(os.path.join(img_dir_true,img))] + [os.path.join(img_dir_false,img) for img in os.listdir(img_dir_false) if os.path.isfile(os.path.join(img_dir_false,img))]
        self.labels = [1]*len(os.listdir(img_dir_true)) + [0]*len(os.listdir(img_dir_false))
    def __len__(self):
        return len(self.img_dirs)

    def __getitem__(self, idx):   
        batch = {"data" :torch.transpose(torch.tensor(imageio.imread(self.img_dirs[idx])),0,2).float() , "labels" : torch.tensor(self.labels[idx])}        
        return [batch]
