from flask import Flask
from flask_restful import Api
from sqlalchemy_utils import database_exists
from api.api import UserAPI

from application.config import LocalDevelopmentConfig  # for configuration of Flask App
from api.database import db  # importing SQLAlchemy instance


def create_app():
    app = Flask(__name__)
    app.config.from_object(
        LocalDevelopmentConfig
    )  # setting the configuration of Flask App

    db.init_app(app)  # for database setup

    api = Api(app)  # Main entry point for the application (with api)

    with app.app_context():
        if not database_exists(app.config["SQLALCHEMY_DATABASE_URI"]):
            db.create_all()

    # above code creates the database if it does not exist

    app.app_context().push()  # creating and pushing context so that it can be used in other files
    return app, api


app, api = create_app()

from application.controllers import *  # importing all the route controllers

api.add_resource(UserAPI, "/api/user", "/api/user/<string:username>")

if __name__ == "__main__":
    app.run(port=8000)  # running the app at port 8000
