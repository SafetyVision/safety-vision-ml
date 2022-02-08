import flask
import json
import boto3
from flask import request
import capturing
import training
import os
import time
import inference
import torch
import HatNoHat
import cv2
import threading
import torchvision
import connection
import requests

app = flask.Flask(__name__)
app.config["DEBUG"] = False
global threads_dict
threads_dict = dict()

@app.route('/train_new', methods=['POST'])
def train_new():
    req = request.get_json()
    kvs_arn = req["kvs_arn"]
    infraction_type = str(req["infraction_type"])
    account_id = str(req["account_id"])
    location = str(req["location"])
    if "output_url" in req:
        output_url = req["output_url"]
    else:
        output_url = "https://safety-vision.ca/api/infraction_events/create"


    pos_dir, neg_dir = capturing.collection_management(
        kvs_arn,
        infraction_type,
        account_id,
        location,
        num_captures=20,
        capture_delay=0.2,
        begin_neg_delay=20,
        begin_pos_delay=20,
    )

    model_dir = training.run_training(
        pos_dir,
        neg_dir,
        model_dir= f'tmp/capstone/{account_id}/{infraction_type}/{location}'
        eval_size=20,
    )

    url = connection.initialize_new_stream(kvs_arn)
    threads_dict[f"{account_id}/{infraction_type}/{location}"] = True
    
    thr = threading.Thread(
        target = inference.run_inference,
        args = (
            infraction_type,
            location,
            url,
            model_dir,
            account_id,
            kvs_arn,
            output_url,
            threads_dict
            )
        )
    thr.start()
    return {"message": "Accepted"}, 202


@app.route('/stop_predicting', methods=['POST'])
def stop_predicting():
    req = request.get_json()
    infraction_type = str(req["infraction_type"])
    account_id = str(req["account_id"])
    location = str(req["location"])
    threads_dict[f"{account_id}/{infraction_type}/{location}"] = False
    return {"message": "Accepted"}, 202
    
@app.route('/restart_predicting', methods = ['POST'])
def restart_predicting():
    req = request.get_json()
    kvs_arn = req["kvs_arn"]
    infraction_type = str(req["infraction_type"])
    account_id = str(req["account_id"])
    location = str(req["location"])
    model_dir= f'tmp/capstone/{account_id}/{infraction_type}/{location}'+'/trained.ckpt'
    if "output_url" in req:
        output_url = req["output_url"]
    else:
        output_url = "https://safety-vision.ca/api/infraction_events/create"
    threads_dict[f"{account_id}/{infraction_type}/{location}"] = True
    url = connection.initialize_new_stream(kvs_arn)
    thr = threading.Thread(
    target = inference.run_inference,
    args = (
        infraction_type,
        location,
        url,
        model_dir,
        account_id,
        kvs_arn,
        output_url,
        threads_dict
        )
    )
    thr.start()
    return {"message": "Accepted"}, 202


@app.route('/inference_route', methods=['POST'])
def inference_route():
    req = request.get_json()
    kvs_arn = req["kvs_arn"]
    infraction_type = str(req["infraction_type"])
    account_id = str(req["account_id"])
    location = str(req["location"])
    model_dir= f'tmp/capstone/{account_id}/{infraction_type}/{location}'+'/trained.ckpt'
    if "output_url" in req:
        output_url = req["output_url"]
    else:
        output_url = "https://safety-vision.ca/api/infraction_events/create"
    threads_dict[f"{account_id}/{infraction_type}/{location}"] = True
    url = connection.initialize_new_stream(kvs_arn)
    thr = threading.Thread(
    target = inference.run_inference,
    args = (
        infraction_type,
        location,
        url,
        model_dir,
        account_id,
        kvs_arn,
        output_url,
        threads_dict
        )
    )
    thr.start()
    return {"message": "Accepted"}, 202

app.run('0.0.0.0',port=5000, threaded=True)
