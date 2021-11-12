from flask_restful import Resource, reqparse
from api.models import User
from api.database import db
from api.validation import BusinessValidationError

create_user_parser = reqparse.RequestParser()
create_user_parser.add_argument("username")
create_user_parser.add_argument("email")
create_user_parser.add_argument("password")


class UserAPI(Resource):
    def get(self, user_id):
        user = User.query.filter(User.user_id == user_id).first()

        if user is None:
            return {"error": "User with username does not exist"}, 306

        return {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
        }

    def post(self):
        args = create_user_parser.parse_args()
        username = args.get("username", None)
        email = args.get("email", None)
        password = args.get("password", None)

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

        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        return {
            "user_id": new_user.user_id,
            "username": new_user.username,
            "email": new_user.email,
            "password": new_user.password,
        }
