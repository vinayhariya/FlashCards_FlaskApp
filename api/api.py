from flask_restful import Resource, reqparse
from api.models import User
from api.database import db
from api.validation import BusinessValidationError
import secrets

entry_user_parser = reqparse.RequestParser()
entry_user_parser.add_argument("username")
entry_user_parser.add_argument("email")
entry_user_parser.add_argument("password")
entry_user_parser.add_argument("new")


class UserAPI(Resource):
    def get(self, user_id):
        user = User.query.filter(User.user_id == user_id).first()

        if user is None:
            return {"error": "User with username does not exist"}, 404

        return {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "api_key": user.api_key,
        }

    def post(self):
        args = entry_user_parser.parse_args()

        username = args["username"]
        password = args["password"]

        if args["new"] == str(True):  # new user trying to get created

            email = args["email"]

            if username is None:
                raise BusinessValidationError(
                    status_code=400,
                    error_code="something",
                    error_message="username is required",
                )

            if email is None:
                raise BusinessValidationError(
                    status_code=400,
                    error_code="something",
                    error_message="email is required",
                )

            if password is None:
                raise BusinessValidationError(
                    status_code=400,
                    error_code="something",
                    error_message="password is required",
                )

            user = User.query.filter(
                (User.username == username) | (User.email == email)
            ).first()

            if user:
                raise BusinessValidationError(
                    status_code=401, error_code="else", error_message="duplicate user"
                )

            api_key = secrets.token_urlsafe(16)

            while User.query.filter(User.api_key == api_key).first():
                api_key = secrets.token_urlsafe(16)

            new_user = User(
                username=username, email=email, password=password, api_key=api_key
            )
            db.session.add(new_user)
            db.session.commit()

            return {
                "user_id": new_user.user_id,
                "username": new_user.username,
                "email": new_user.email,
                "password": new_user.password,
            }
        else:  # user trying to log in
            if username is None:
                raise BusinessValidationError(
                    status_code=400,
                    error_code="something",
                    error_message="username is required",
                )

            if password is None:
                raise BusinessValidationError(
                    status_code=400,
                    error_code="something",
                    error_message="password is required",
                )

            user = User.query.filter(
                (User.username == username) & (User.password == password)
            ).first()

            if user:
                return {"status": 200, "logged_in": True}
            else:
                raise BusinessValidationError(
                    status_code=401,
                    error_code="else",
                    error_message="login error, details do not match",
                )
