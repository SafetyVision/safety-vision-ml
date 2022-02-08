import time
import cv2
import os
import connection
import shutil

def collection_management(kvs_arn, infraction_type, account_id, location, num_captures, capture_delay, begin_neg_delay, begin_pos_delay):
    if os.path.isdir(f'tmp/capstone/{account_id}/{infraction_type}/{location}'):
        shutil.rmtree(f'tmp/capstone/{account_id}/{infraction_type}/{location}')

    url = connection.initialize_new_stream(kvs_arn)
    print(f'Starting positive images collection in {begin_pos_delay} seconds')
    time.sleep(begin_pos_delay)
    print('Starting positive images collection')
    pos_dir = begin_collection(url, infraction_type, account_id, location, capture_delay, "positive", num_captures)

    url = connection.initialize_new_stream(kvs_arn)
    print(f'Starting negative images collection in {begin_neg_delay} seconds')
    time.sleep(begin_neg_delay)
    print('Starting negative images collection')
    neg_dir = begin_collection(url, infraction_type, account_id, location, capture_delay, "negative", num_captures)
    print('Image collection complete')

    return (pos_dir, neg_dir)

def begin_collection(url, infraction_type, account_id, location, capture_delay, positive_negative, num_frames):
    count = 0
    os.makedirs(f'tmp/capstone/{account_id}/{infraction_type}/{location}/{positive_negative}', exist_ok=True)    
    while count < num_frames:
        cap = cv2.VideoCapture(url)
        ret, frame = cap.read()
        frame = cv2.resize(frame, (224,224))        
        cv2.imwrite(f'tmp/capstone/{account_id}/{infraction_type}/{location}/{positive_negative}/img{count}.png',frame)
        count += 1
        print(count)
        time.sleep(capture_delay)
    return f'tmp/capstone/{account_id}/{infraction_type}/{location}/{positive_negative}' 
    
