import torchvision
import requests
import HatNoHat
import cv2
import time
import torch
import requests 
from datetime import datetime
import connection
def inference(infraction_type, location, url, model_path, account_id,kvs_arn ):
    M = torch.nn.Sigmoid()
    with torch.no_grad():
        model2 =  torchvision.models.mobilenet_v2(pretrained=True)
        model2.classifier[1] = torch.nn.Linear(in_features=model2.classifier[1].in_features,out_features=1)
        model = HatNoHat.HatNoHat.load_from_checkpoint(model_path,model=model2)
        while(True):
            try:
                cap = cv2.VideoCapture(url)
                ret, frame = cap.read()
                frame = cv2.resize(frame, (224,224)) 
                ft = torch.tensor(frame)
                ft = torch.transpose(ft,0,2)
                ft= ft.unsqueeze(0)
                out = model.forward(ft.float())
                out = M(out)
                if out.numpy().tolist()[0][0] > 0.7:
                    now = datetime.now()
                    dt_string = now.strftime("%Y-%m-%dT%H:%M:%S-05:00") #Yes I know I hardcoded a time zone sue me
                    send_infraction(dt_string,account_id)
                    print('hi there')
                time.sleep(1)
            except cv2.error:
                url = connection.initialize_new_stream(kvs_arn)
                continue


def send_infraction(dt,account):
    URL = "https://safety-vision.ca/api/infraction_events/create"
    requests.post(url = URL, json={"infraction_date_time":dt, "account":account}, headers={'Content-Type: application/json','x-create-infraction-event-key": "token'})

