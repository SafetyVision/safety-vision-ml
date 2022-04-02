import torch
import imageio
import os
from torch.utils.data import Dataset
from torchvision import transforms as tr

pipeline = tr.Compose(
             [tr.RandomRotation(degrees = 90),
              tr.RandomRotation(degrees = 270)])


class DemonstrationImageDataset(Dataset):
    def __init__(self,img_dir_true,img_dir_false):
        self.img_dirs = [os.path.join(img_dir_true,img) for img in os.listdir(img_dir_true)] + [os.path.join(img_dir_false,img) for img in os.listdir(img_dir_false)]
        self.labels = [1]*len(os.listdir(img_dir_true)) + [0]*len(os.listdir(img_dir_false))
    def __len__(self):
        return len(self.img_dirs)

    def __getitem__(self, idx):   
        batch = {"data" :pipeline(torch.transpose(torch.tensor(imageio.imread(self.img_dirs[idx])),0,2).float()) , "labels" : torch.tensor(self.labels[idx])}        
        return [batch]
