import flask
import json
import boto3
from flask import request
import capturing
import training
import os
import time
#import celery
import inference
import torch
import HatNoHat
import cv2
import threading
import torchvision
import connection


app = flask.Flask(__name__)
app.config["DEBUG"] = False
#celery = celery.Celery(app.name)

@app.route('/predict', methods=['POST'])
def predict():
    print(request.data)
    time.sleep(10)
    return ""

@app.route('/train_new', methods=['POST'])
def train_new():
    req = request.get_json()
    kvs_arn = req["kvs_arn"]
    infraction_type = req["infraction_type"]
    account_id = req["account_id"]
    location = req["location"]
    #url = initialize_new_stream(kvs_arn)
    print('starting pos in 10 seconds')
    time.sleep(10)
    print('starting pos')
    url = connection.initialize_new_stream(kvs_arn)
    pos_dir = capturing.begin_collection(url,req["infraction_type"],"positive",200)
    print('starting neg in 10 seconds')
    time.sleep(10)
    print('starting neg')
    url = connection.initialize_new_stream(kvs_arn)
    neg_dir = capturing.begin_collection(url,req["infraction_type"],"negative",200)
    model_dir = training.run_training(pos_dir, neg_dir,f'./tmp/capstone/{req["infraction_type"]}',20)

    url = connection.initialize_new_stream(kvs_arn)
    thr = threading.Thread(target = inference.inference, args=(infraction_type, location, url, model_dir, account_id,kvs_arn))
    thr.start()
    




app.run('0.0.0.0',port=5000)