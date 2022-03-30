import boto3
import os

from constants import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, REGION

def initialize_new_stream(kvs_arn):
    kvs_client = boto3.client(
        'kinesisvideo',
        aws_access_key_id= AWS_ACCESS_KEY_ID,
        aws_secret_access_key= AWS_SECRET_ACCESS_KEY,
        region_name= REGION
        )
    kvs_endpoint = kvs_client.get_data_endpoint(
        StreamARN=kvs_arn,
        APIName="GET_HLS_STREAMING_SESSION_URL"
    )
    endpoint_url = kvs_endpoint['DataEndpoint']
    media_client = boto3.client(
        'kinesis-video-archived-media',
        aws_access_key_id = AWS_ACCESS_KEY_ID,
        aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
        endpoint_url=endpoint_url,
        region_name= REGION
    )
    url = media_client.get_hls_streaming_session_url(
        StreamARN=kvs_arn,
        PlaybackMode='LIVE'
    )["HLSStreamingSessionURL"]

    return url