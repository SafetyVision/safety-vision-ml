import threading
import time
import cv2
import os
import connection
import shutil
import requests

from constants import MODEL_BASE_DIR, PLATFORM_ENDPOINT, TOKEN
from request import post_request

def collection_management(parsed_details, train_request, begin_positive, begin_negative, continue_number=0, wait_request=True):
    if os.path.isdir(f'{MODEL_BASE_DIR}/{parsed_details.details_string}') and continue_number == 0:
        shutil.rmtree(f'{MODEL_BASE_DIR}/{parsed_details.details_string}')

    start = time.time()
    while(begin_positive[parsed_details.details_string] == False and wait_request):
        time.sleep(0.5)
        if(time.time()-start) > 300:
            raise TimeoutError("Waited too long to begin collection")                

    url = connection.initialize_new_stream(parsed_details.kvs_arn)
    print(f'Starting positive images collection in {train_request.stream_delay} seconds')
    time.sleep(train_request.stream_delay)
    print('Starting positive images collection')
    pos_dir = begin_collection(url, parsed_details, train_request, "positive", 1, continue_number)
    send_done_commit(parsed_details)

    start = time.time()
    while(begin_negative[parsed_details.details_string] == False and wait_request):
        time.sleep(0.5)    
        if(time.time()-start) > 300:
            raise TimeoutError("Waited too long to begin collection")   

    url = connection.initialize_new_stream(parsed_details.kvs_arn)
    print(f'Starting negative images collection in {train_request.stream_delay} seconds')
    time.sleep(train_request.stream_delay)
    print('Starting negative images collection')
    neg_dir = begin_collection(url, parsed_details, train_request, "negative", 1, continue_number)
    send_done_not_commit(parsed_details)

    start = time.time()
    while(begin_positive[parsed_details.details_string] == False and wait_request):
        time.sleep(0.5)
        if(time.time()-start) > 300:
            raise TimeoutError("Waited too long to begin collection")                

    url = connection.initialize_new_stream(parsed_details.kvs_arn)
    print(f'Starting positive images collection in {train_request.stream_delay} seconds')
    time.sleep(train_request.stream_delay)
    print('Starting positive images collection')
    pos_dir = begin_collection(url, parsed_details, train_request, "positive", 2, continue_number)
    send_done_commit(parsed_details)

    start = time.time()
    while(begin_negative[parsed_details.details_string] == False and wait_request):
        time.sleep(0.5)    
        if(time.time()-start) > 300:
            raise TimeoutError("Waited too long to begin collection")   

    url = connection.initialize_new_stream(parsed_details.kvs_arn)
    print(f'Starting negative images collection in {train_request.stream_delay} seconds')
    time.sleep(train_request.stream_delay)
    print('Starting negative images collection')
    neg_dir = begin_collection(url, parsed_details, train_request, "negative", 2, continue_number)
    send_done_not_commit(parsed_details)
    print('Image collection complete')
    

def begin_collection(url, parsed_details, train_request, positive_negative, series_number, continue_number):
    iter_end = series_number * (train_request.num_captures // 4)
    os.makedirs(f'{MODEL_BASE_DIR}/{parsed_details.details_string}/{positive_negative}', exist_ok=True)
    iter_start = (series_number-1) * (train_request.num_captures // 4)
    while iter_start < iter_end:
        cap = cv2.VideoCapture(url)
        ret, frame = cap.read()
        frame = cv2.resize(frame, (224,224))        
        cv2.imwrite(f'{MODEL_BASE_DIR}/{parsed_details.details_string}/{positive_negative}/{continue_number}img{iter_start}.png',frame)
        iter_start += 1
        print(iter_start)
        time.sleep(train_request.between_captures)
    return f'{MODEL_BASE_DIR}/{parsed_details.details_string}/{positive_negative}' 
    

def send_capturing_failure(parsed_details):
    post_request(
        parsed_details,
        options = {"currently_tracking" : True},
        url = f'{PLATFORM_ENDPOINT}{parsed_details.device_serial_number}/infraction_types/{parsed_details.infraction_type_id}/needs_retraining',
    )

def send_done_commit(parsed_details):
    post_request(
        parsed_details,
        options = {"currently_tracking" : True},
        url = f'{PLATFORM_ENDPOINT}{parsed_details.device_serial_number}/infraction_types/{parsed_details.infraction_type_id}/done_commit',
    )

def send_done_not_commit(parsed_details):
    post_request(
        parsed_details,
        options = {"currently_tracking" : True},
        url = f'{PLATFORM_ENDPOINT}{parsed_details.device_serial_number}/infraction_types/{parsed_details.infraction_type_id}/done_not_commit',
    )