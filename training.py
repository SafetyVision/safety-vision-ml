import os
import imageio
import pandas as pd
from torchvision.io import read_image
import torch
from torch.utils.data import Dataset, DataLoader
import torchvision
import pytorch_lightning as pl
import requests
from constants import MODEL_BASE_DIR, TOKEN, TRAINED_NAME

from dataset import DemonstrationImageDataset
from model import InfractionDetectionModel


def col_fn(batch):
    out = dict()
    out['data'] = torch.stack([x['data'] for x in batch[0]])
    out['labels'] = torch.stack([x['labels'] for x in batch[0]])
    return out

def run_training(parsed_details, train_request):
    model_dir= f'{MODEL_BASE_DIR}/{parsed_details.details_string}'

    dataset = DemonstrationImageDataset(
        img_dir_true = os.path.join(model_dir,"positive"),
        img_dir_false = os.path.join(model_dir,"negative"),
        )

    train_set, val_set = torch.utils.data.random_split(
        dataset,
        [len(dataset)-train_request.eval_size, train_request.eval_size],
        )

    model =  torchvision.models.mobilenet_v2(pretrained=True)
    model.classifier[1] = torch.nn.Linear(in_features=model.classifier[1].in_features,out_features=1)
    agh = InfractionDetectionModel(train_set, val_set, model, col_fn) 
    trainer = pl.Trainer(max_epochs=2)
    print('begin training')
    trainer.fit(agh)
    print(trainer)

    trainer.save_checkpoint(os.path.join(model_dir, TRAINED_NAME))
    send_training_complete(parsed_details)
    return os.path.join(model_dir,TRAINED_NAME)

def send_training_complete(parsed_details):
    requests.post(
        url = f'{parsed_details.device_serial_number}/infraction_types/{parsed_details.infraction_type_id}/training_complete',
        json={
            "device_serial_number" : parsed_details.device_serial_number,
            "infraction_type_id" : parsed_details.infraction_type_id,
            "training_complete" : True,
        },
        headers={
            "Content-Type": "application/json",
            "x-create-infraction-event-key": TOKEN
        }
    )

def send_training_failure(parsed_details):
    requests.post(
        url = f'{parsed_details.device_serial_number}/infraction_types/{parsed_details.infraction_type_id}/needs_retraining',
        json={
            "device_serial_number" : parsed_details.device_serial_number,
            "infraction_type_id" : parsed_details.infraction_type_id,
            "currently_tracking" : True,
        },
        headers={
            "Content-Type": "application/json",
            "x-create-infraction-event-key": TOKEN
        }
    )