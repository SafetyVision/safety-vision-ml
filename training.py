import os
import imageio
import pandas as pd
from torchvision.io import read_image
import torch
from torch.utils.data import Dataset, DataLoader
import torchvision
import pytorch_lightning as pl
import requests

from CustomImageDataset import CustomImageDataset
from HatNoHat import HatNoHat


def col_fn(batch):
    out = dict()
    out['data'] = torch.stack([x['data'] for x in batch[0]])
    out['labels'] = torch.stack([x['labels'] for x in batch[0]])
    return out

def run_training(pos_dir,neg_dir,model_dir,eval_size,infraction_type,location,account_id,output_url):
    dataset = CustomImageDataset(img_dir_true = pos_dir, img_dir_false = neg_dir)
    train_set, val_set = torch.utils.data.random_split(dataset, [len(dataset)-eval_size, eval_size])
    model =  torchvision.models.mobilenet_v2(pretrained=True)
    model.classifier[1] = torch.nn.Linear(in_features=model.classifier[1].in_features,out_features=1)
    agh = HatNoHat(train_set, val_set, model, col_fn) 
    trainer = pl.Trainer(max_epochs=2)
    print('begin training')
    trainer.fit(agh)
    trainer.save_checkpoint(os.path.join(model_dir,'trained.ckpt'))
    send_training_complete(infraction_type,location,account_id,output_url)
    return os.path.join(model_dir,'trained.ckpt')

def send_training_complete(infraction_type,location,account_id,output_url):
    token = os.environ["PLATFORM_TOKEN"]
    requests.post(
        url = output_url,
        json={
            "account" : account_id,
            "location" : location,
            "infraction_type" : infraction_type,
            "training_complete" : True,
        },
        headers={
            "Content-Type": "application/json",
            "x-create-infraction-event-key": token
        }
    )
