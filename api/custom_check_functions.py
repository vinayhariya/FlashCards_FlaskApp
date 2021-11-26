from api.models import User
from api.validation import MissingParameterError


def check_username(username):
    if username is None or username.strip() == '':
        raise MissingParameterError(error_message="User Name is required")

    return username.strip().title()


def check_password(password):
    if password is None or password.strip() == '':
        raise MissingParameterError(error_message="Password is required")

    return password.strip()


def check_email(email):
    if email is None or email.strip() == '':
        raise MissingParameterError(error_message="Email is required")

    email = email.strip()

    if '@' not in email:
        raise MissingParameterError(error_message="@ is required in email")

    return email


def checkUserValid(user_id, api_key):
    return User.query.filter((User.user_id == user_id) & (User.api_key == api_key)).first() is not None
