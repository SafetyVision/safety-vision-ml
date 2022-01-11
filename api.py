import flask
from flask import request

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/predict', methods=['POST'])
def predict():
    print(request.data)
    return ""

@app.route('/train', methods=['GET'])
def train():
    return ""

app.run()