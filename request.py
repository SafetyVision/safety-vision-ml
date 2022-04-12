import requests
from constants import TOKEN

def post_request(parsed_details, options, url):
    json_dict = {
        "device_serial_number" : parsed_details.device_serial_number,
        "infraction_type_id" : parsed_details.infraction_type_id
    }
    requests.post(
        url = url,
        json={**json_dict, **options},
        headers={
            "Content-Type": "application/json",
            "x-create-infraction-event-key": TOKEN
        }
    )