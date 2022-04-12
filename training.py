import os
import imageio
import pandas as pd
from torchvision.io import read_image
import torch
from torch.utils.data import Dataset, DataLoader
import torchvision
import pytorch_lightning as pl
import requests
from constants import MODEL_BASE_DIR, PLATFORM_ENDPOINT, TOKEN, TRAINED_NAME

from dataset import DemonstrationImageDataset
from model import InfractionDetectionModel
from request import post_request


def col_fn(batch):
    out = dict()
    out['data'] = torch.stack([x['data'] for x in batch[0]])
    out['labels'] = torch.stack([x['labels'] for x in batch[0]])
    return out

def run_training(parsed_details, train_request, allow_bad = False):
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
    trainer.fit(agh)
    validate_results = trainer.validate()
    print(validate_results)
    if validate_results[0]['precision'] < 0.9 or validate_results[0]['precision'] < 0.9:
        print('Training failure, please try again')
        trainer.save_checkpoint(os.path.join(model_dir, TRAINED_NAME))
        send_training_failure(parsed_details)
        if allow_bad:
            return os.path.join(model_dir,TRAINED_NAME)
        else:
            return None
    else:
        trainer.save_checkpoint(os.path.join(model_dir, TRAINED_NAME))
        send_training_complete(parsed_details)
        return os.path.join(model_dir,TRAINED_NAME)

def send_training_complete(parsed_details):
    post_request(
        parsed_details,
        options = {"training_complete" : True},
        url = f'{PLATFORM_ENDPOINT}{parsed_details.device_serial_number}/infraction_types/{parsed_details.infraction_type_id}/training_complete',
    )

def send_training_failure(parsed_details):
    post_request(
        parsed_details,
        options = {"training_complete" : False},
        url = f'{PLATFORM_ENDPOINT}{parsed_details.device_serial_number}/infraction_types/{parsed_details.infraction_type_id}/needs_retraining',
    )