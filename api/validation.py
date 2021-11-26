from werkzeug.exceptions import HTTPException
from flask import make_response
import json


class MissingParameterError(HTTPException):
    def __init__(self, error_message):
        status_code = 400  # 404 Bad Request
        data = {
            "status_code": status_code,
            "error_message": error_message
        }
        self.response = make_response(json.dumps(data), status_code)


class LoginError(HTTPException):
    def __init__(self, error_message):
        status_code = 401  # 401 Unauthorized
        data = {
            "status_code": status_code,
            "error_message": error_message
        }
        self.response = make_response(json.dumps(data), status_code)


class UnauthenticatedUserError(HTTPException):
    def __init__(self, error_message):
        status_code = 401  # 401 Unauthenticated
        data = {
            "status_code": status_code,
            "error_message": error_message
        }
        self.response = make_response(json.dumps(data), status_code)


class DoesNotExistError(HTTPException):
    def __init__(self, error_message):
        status_code = 404  # 404 Not Found
        data = {
            "status_code": status_code,
            "error_message": error_message
        }
        self.response = make_response(json.dumps(data), status_code)


class NotAllowedError(HTTPException):
    def __init__(self, error_message):
        status_code = 403  # 403 Forbidden
        data = {
            "status_code": status_code,
            "error_message": error_message
        }
        self.response = make_response(json.dumps(data), status_code)
