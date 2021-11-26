from werkzeug.exceptions import HTTPException
from flask import make_response
import json
# TODO change this accordingly

class BusinessValidationError(HTTPException): # put proper validationn
    def __init__(self, status_code, error_code, error_message):
        data = {
            "error_code": error_code,
            "error_message": error_message,
        }
        self.response = make_response(json.dumps(data), status_code)
