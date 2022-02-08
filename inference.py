import torchvision
import requests
import HatNoHat
import cv2
import time
import torch
import requests 
import datetime
import connection
import os

def run_inference(infraction_type, location, url, model_path, account_id,kvs_arn, output_url, threads_dict):
    M = torch.nn.Sigmoid()
    token = os.environ["PLATFORM_TOKEN"]
    with torch.no_grad():
        model_init =  torchvision.models.mobilenet_v2(pretrained=False)
        model_init.classifier[1] = torch.nn.Linear(in_features=model_init.classifier[1].in_features,out_features=1)
        model = HatNoHat.HatNoHat.load_from_checkpoint(model_path,model=model_init)
        send_begin_detection(account_id, location, infraction_type, token, output_url)
        while(threads_dict[f"{account_id}/{infraction_type}/{location}"] == True):
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
                if out.numpy().tolist()[0][0] > 0.50:
                    now = datetime.datetime.now()
                    dt_string = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) - datetime.timedelta(seconds=15)
                    dt_string = dt_string.isoformat()
                    send_infraction(dt_string,account_id,location, infraction_type,token,output_url)
                time.sleep(1)
            except cv2.error:
                url = connection.initialize_new_stream(kvs_arn)
                continue
        send_end_detection(account_id, location, infraction_type, token, output_url)


def send_infraction(dt, account_id, location, infraction_type, token, output_url):
    requests.post(
        url = output_url,
        json={
            "infraction_date_time":dt,
            "account" : account_id,
            "location" : location,
            "infraction_type" : infraction_type,
        },
        headers={
            "Content-Type": "application/json",
            "x-create-infraction-event-key": token
        }
    )

def send_begin_detection(account_id, location, infraction_type, token, output_url):
    requests.post(
        url = output_url,
        json={
            "account" : account_id,
            "location" : location,
            "infraction_type" : infraction_type,
            "currently_tracking" : True,
        },
        headers={
            "Content-Type": "application/json",
            "x-create-infraction-event-key": token
        }
    )

def send_end_detection(account_id, location, infraction_type, token, output_url):
    requests.post(
        url = output_url,
        json={
            "account" : account_id,
            "location" : location,
            "infraction_type" : infraction_type,
            "currently_tracking" : False,
        },
        headers={
            "Content-Type": "application/json",
            "x-create-infraction-event-key": token
        }
    )