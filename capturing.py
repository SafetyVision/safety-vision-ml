import time
import cv2
import os

def begin_collection(url,infraction_type,positive_negative):
    count = 0
    os.makedirs(f'tmp/capstone/{infraction_type}/{positive_negative}', exist_ok=True)
    while count < 20:
        cap = cv2.VideoCapture(url)
        ret, frame = cap.read()
        frame = cv2.resize(frame, (224,224))        
        cv2.imwrite(f'./tmp/capstone/{infraction_type}/{positive_negative}/img{count}.png',frame)
        count += 1
        #time.sleep(0.5)
    print('Done capurue')
    return f'./tmp/capstone/{infraction_type}/{positive_negative}' 
    