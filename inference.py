import torchvision
import requests
from constants import TOKEN
import model
import cv2
import time
import torch
import requests 
import datetime
import connection
import os
from model import InfractionDetectionModel

def run_inference(parsed_details, train_request, url, model_path, threads_dict):
    M = torch.nn.Sigmoid()
    with torch.no_grad():
        #Loading model and making binary classifier
        model_init =  torchvision.models.resnet50(pretrained=False)
        model_init.fc = torch.nn.Linear(in_features=model_init.fc.in_features,out_features=1)
        model = InfractionDetectionModel.load_from_checkpoint(model_path,model=model_init)
        model.eval()
        print(model)

        #send_begin_detection(parsed_details)
        while(threads_dict[parsed_details.details_string] == True):
            try:
                cap = cv2.VideoCapture(url)
                ret, frame = cap.read()
                frame = cv2.resize(frame, (224,224)) 
                ft = torch.tensor(frame)
                ft = torch.transpose(ft,0,2)
                ft= ft.unsqueeze(0)
                out = model.forward(ft.float())
                out = M(out)
                print(out.numpy().tolist()[0][0])
                if out.numpy().tolist()[0][0] > 0.60:
                    dt_string = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) - datetime.timedelta(seconds=train_request.stream_delay)
                    dt_string = dt_string.isoformat()                   
                    send_infraction(dt_string, parsed_details)
                    time.sleep(10)
                time.sleep(1)
            except cv2.error:
                url = connection.initialize_new_stream(parsed_details.kvs_arn)
                continue
        #send_end_detection(parsed_details)


def send_infraction(dt_string, parsed_details):
    requests.post(
        url = parsed_details.output_url,
        json={
            "infraction_date_time":dt_string,
            "device" : parsed_details.device_serial_number,
            "infraction_type" : int(parsed_details.infraction_type_id),
        },
        headers={
            "Content-Type": "application/json",
            "x-create-infraction-event-key": TOKEN
        }
    )

def send_begin_detection(parsed_details):
    requests.post(
        url = parsed_details.output_url,
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

def send_end_detection(parsed_details):
    requests.post(
        url = parsed_details.output_url,
        json={
            "device_serial_number" : parsed_details.device_serial_number,
            "infraction_type_id" : parsed_details.infraction_type_id,
            "currently_tracking" : False,
        },
        headers={
            "Content-Type": "application/json",
            "x-create-infraction-event-key": TOKEN
        }
    )