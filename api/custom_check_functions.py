from api.models import User
from api.validation import BusinessValidationError
# TODO change this accordingly

def check_username(username):
    if username is None or username.strip() == '':
        raise BusinessValidationError(
            status_code=505,
            error_code="something",
            error_message="username is required",
        )

    return username.strip()


def check_password(password):
    if password is None or password.strip() == '':
        raise BusinessValidationError(
            status_code=505,
            error_code="something",
            error_message="password is required",
        )

    return password.strip()


def check_email(email):
    if email is None or email.strip() == '':
        raise BusinessValidationError(
            status_code=505,
            error_code="something",
            error_message="email is required",
        )

    email = email.strip()

    if '@' not in email:
        raise BusinessValidationError(
            status_code=505,
            error_code="something",
            error_message="@ is required in email",
        )

    return email


def invalidUserCred():
    raise BusinessValidationError(
        status_code=605,
        error_code="something",
        error_message="invalid user cred !!!!",
    )


def checkUserValid(user_id, api_key):
    return User.query.filter((User.user_id == user_id) & (User.api_key == api_key)).first() is not None
