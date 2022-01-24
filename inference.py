import celery
import requests
import HatNoHat
import cv2
import time
import torch
@celery.task
def inference(infraction_type, location, url, model_path ):
    M = torch.nn.Sigmoid()
    with torch.no_grad():
        model = HatNoHat.HatNoHat.load_from_checkpoint(model_path)
        while(True):
            cap = cv2.VideoCapture(url)
            ret, frame = cap.read()
            frame = cv2.resize(frame, (224,224)) 
            ft = torch.tensor(frame)
            ft = torch.transpose(ft,0,2)
            ft= ft.unsqueeze(0)
            out = model.forward(ft.float())
            out = M(out)
            if out.numpy().tolist()[0][0] > 0.5:
                print('hi there')
            time.sleep(1)
