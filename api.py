import flask
import json
import boto3
from flask import request
import capturing
import training
import os
import time
import celery
import inference

def initialize_new_stream(kvs_arn):
    kvs_client = boto3.client(
        'kinesisvideo',
        aws_access_key_id = os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key =  os.environ["AWS_SECRET_ACCESS_KEY"],
        region_name= "us-east-1")
    kvs_endpoint = kvs_client.get_data_endpoint(
        StreamARN=kvs_arn,
        APIName="GET_HLS_STREAMING_SESSION_URL"
    )
    endpoint_url = kvs_endpoint['DataEndpoint']
    media_client = boto3.client(
        'kinesis-video-archived-media',
        aws_access_key_id = os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key = os.environ["AWS_SECRET_ACCESS_KEY"],
        endpoint_url=endpoint_url,
        region_name= "us-east-1"
    )
    url = media_client.get_hls_streaming_session_url(
        StreamARN=kvs_arn,
        PlaybackMode='LIVE'
    )["HLSStreamingSessionURL"]

    return url

app = flask.Flask(__name__)
app.config["DEBUG"] = True
celery = celery.Celery(app.name)

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
    url = initialize_new_stream(kvs_arn)
    print('starting pos in 5 seconds')
    time.sleep(5)
    pos_dir = capturing.begin_collection(url,req["infraction_type"],"positive")
    print('starting neg in 5 seconds')
    time.sleep(5)
    neg_dir = capturing.begin_collection(url,req["infraction_type"],"negative")
    model_dir = training.run_training(pos_dir, neg_dir,f'./tmp/capstone/{req["infraction_type"]}',20)
    inference.inference.delay(infraction_type, location, url, model_dir)
    return ""


app.run('0.0.0.0',port=5000)