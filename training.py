import os
import imageio
import pandas as pd
from torchvision.io import read_image
import torch
from torch.utils.data import Dataset, DataLoader
import torchvision
import pytorch_lightning as pl

from CustomImageDataset import CustomImageDataset
from HatNoHat import HatNoHat


def col_fn(batch):
    out = dict()
    out['data'] = torch.stack([x['data'] for x in batch[0]])
    out['labels'] = torch.stack([x['labels'] for x in batch[0]])
    return out

def run_training(pos_dir,neg_dir):
    dataset = CustomImageDataset(img_dir_true = pos_dir, img_dir_false = neg_dir)
    train_set, val_set = torch.utils.data.random_split(dataset, [30, 10])
    model =  torchvision.models.mobilenet_v2(pretrained=True)
    model.classifier[1] = torch.nn.Linear(in_features=model.classifier[1].in_features,out_features=1)
    agh = HatNoHat(train_set, val_set, model, col_fn) 
    trainer = pl.Trainer(max_epochs=2)
    print('begin training')
    trainer.fit(agh)