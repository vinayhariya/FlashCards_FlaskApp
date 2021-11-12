from flask import Flask
from flask_restful import Api
from flask_login import LoginManager
from sqlalchemy_utils import database_exists

from application.config import LocalDevelopmentConfig  # for configuration of Flask App
from api.api import UserAPI
from api.database import db  # importing SQLAlchemy instance
from api.models import User


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

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(
            int(user_id)
        )  # used for maintaining the current user of the app

    from application.auth import auth as auth_blueprint
    from application.main_controllers import main_cont as main_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)

    return app, api


app, api = create_app()

api.add_resource(UserAPI, "/api/user", "/api/user/<int:user_id>")

if __name__ == "__main__":
    app.run(port=8000)  # running the app at port 8000
