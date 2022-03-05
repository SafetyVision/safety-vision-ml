import attr
from functools import cached_property
from typing import Optional

from constants import CREATE_ENDPOINT

@attr.define
class RequestDetails:
    infraction_type_id: Optional[str] = None
    kvs_arn: Optional[str] = None
    device_serial_number: Optional[str] = None
    output_url: Optional[str] = None

    @cached_property
    def details_string(self):
        return f"{self.device_serial_number}/{self.infraction_type_id}"

@attr.define
class TrainRequest:
    num_captures: int = 20,
    between_captures: float = 0.2,
    stream_delay: float = 15,
     
    


def parse_request_details(req):
    return RequestDetails(
        account_id = str(req.get("account_id", None)),
        infraction_type_id = str(req.get("infraction_type_id", None)),
        kvs_arn = str(req.get("kvs_arn", None)),
        device_serial_number = str(req.get("device_serial_number", None)),
        output_url = str(req.get("output_url", CREATE_ENDPOINT)),
    )

def parse_train_details(req):
    return TrainRequest(
        account_id = str(req.get("account_id", None)),
        infraction_type_id = str(req.get("infraction_type_id", None)),
        kvs_arn = str(req.get("kvs_arn", None)),
        device_serial_number = str(req.get("device_serial_number", None)),
        output_url = str(req.get("output_url", CREATE_ENDPOINT)),
    )