import os

MODEL_BASE_DIR = 'tmp/capstone/'
CREATE_ENDPOINT = 'https://safety-vision.ca/api/infraction_events/create'
AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY =  os.environ["AWS_SECRET_ACCESS_KEY"]
REGION = "us-east-1"
TRAINED_NAME = 'trained.ckpt'
TOKEN = os.environ["PLATFORM_TOKEN"]
