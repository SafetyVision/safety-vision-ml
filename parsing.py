import attr
from typing import Optional

from constants import CREATE_ENDPOINT

@attr.define
class RequestDetails:
    infraction_type_id: Optional[str] = None
    kvs_arn: Optional[str] = None
    device_serial_number: Optional[str] = None
    output_url: Optional[str] = None

    @property
    def details_string(self):
        return f"{self.device_serial_number}/{self.infraction_type_id}"

@attr.define
class TrainRequest:
    num_captures: Optional[int]
    between_captures: Optional[float]
    stream_delay: Optional[float]
    eval_size: Optional[float]
      


def parse_request_details(req):
    return RequestDetails(
        infraction_type_id = str(req.get("infraction_type_id", None)),
        kvs_arn = str(req.get("kvs_arn", None)),
        device_serial_number = str(req.get("device_serial_number", None)),
        output_url = str(req.get("output_url", CREATE_ENDPOINT)),
    )

def parse_train_details(req):
    return TrainRequest(
        num_captures = req.get("num_captures", 200),
        between_captures = req.get("between_captures", 0.2),
        stream_delay = req.get("stream_delay", 15.0),
        eval_size = req.get("eval_size", 40),
    )