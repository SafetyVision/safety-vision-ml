import flask
import capturing
import training
import inference
import threading
import connection
from parsing import parse_request_details, parse_train_details
from constants import MODEL_BASE_DIR, TRAINED_NAME

app = flask.Flask(__name__)
app.config["DEBUG"] = False
global threads_dict
global begin_postive
global begin_negative
threads_dict = dict()
begin_positive = dict()
begin_negative = dict()

@app.route('/train_new', methods=['POST'])
def train_new():
    print('start?')
    #Input parsing
    req = flask.request.get_json()
    parsed_details = parse_request_details(req)
    train_request = parse_train_details(req)

    begin_positive[parsed_details.details_string] = False
    begin_negative[parsed_details.details_string] = False
    #Training data collection
    try:
        model_path = None
        continue_number =0
        while model_path is None:
            capturing.collection_management(parsed_details, train_request, begin_positive, begin_negative, continue_number)

            #Model training
            model_path = training.run_training(
                parsed_details,
                train_request
            )
            continue_number += 1

        #Infraction detection
        url = connection.initialize_new_stream(parsed_details.kvs_arn)
        threads_dict[parsed_details.details_string] = True
        thr = threading.Thread(
            target = inference.run_inference,
            args = (
                parsed_details,
                train_request,
                url,
                model_path,
                threads_dict
                )
            )
        thr.start()

        return {"message": "Accepted"}, 202
    except TimeoutError: 
        return {"message": "Accepted"}, 202

@app.route('/train_restart', methods=['POST'])
def train_restart():
    req = flask.request.get_json()
    parsed_details = parse_request_details(req)
    train_request = parse_train_details(req)

    #Model training
    model_path = training.run_training(
        parsed_details,
        train_request
    )

    #Infraction detection
    url = connection.initialize_new_stream(parsed_details.kvs_arn)
    threads_dict[parsed_details.details_string] = True
    thr = threading.Thread(
        target = inference.run_inference,
        args = (
            parsed_details,
            train_request,
            url,
            model_path,
            threads_dict
            )
        )
    thr.start()
    

@app.route('/start_positive', methods=['POST'])
def start_positive():
    #Input parsing
    req = flask.request.get_json()
    parsed_details = parse_request_details(req)
    begin_negative[parsed_details.details_string] = False
    begin_positive[parsed_details.details_string] = True
    return {"message": "Accepted"}, 202

@app.route('/start_negative', methods=['POST'])
def start_negative():
    #Input parsing
    req = flask.request.get_json()
    parsed_details = parse_request_details(req)
    begin_positive[parsed_details.details_string] = False
    begin_negative[parsed_details.details_string] = True
    return {"message": "Accepted"}, 202


@app.route('/stop_predicting', methods=['POST'])
def stop_predicting():
    req = flask.request.get_json()    
    parsed_details = parse_request_details(req)
    threads_dict[parsed_details.details_string] = False
    return {"message": "Accepted"}, 202
    
@app.route('/restart_predicting', methods = ['POST'])
def restart_predicting():
    req = flask.request.get_json()    
    parsed_details = parse_request_details(req)
    train_request = parse_train_details(req)
    model_dir= f'{MODEL_BASE_DIR}/{parsed_details.details_string}/{TRAINED_NAME}'
    threads_dict[parsed_details.details_string] = True
    url = connection.initialize_new_stream(parsed_details.kvs_arn)
    thr = threading.Thread(
        target = inference.run_inference,
        args = (
            parsed_details,
            train_request,
            url,
            model_dir,
            threads_dict
            )
        )
    thr.start()
    return {"message": "Accepted"}, 202

@app.route('/local_requests', methods = ['POST'])
def local_requests():
    req = flask.request.get_json()
    print('--------------')
    print(req)
    print('--------------')
    return ""

app.run('0.0.0.0',port=5000, threaded=True)
