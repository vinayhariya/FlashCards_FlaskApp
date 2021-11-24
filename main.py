from flask import Flask
from flask_restful import Api
from flask_login import LoginManager
from sqlalchemy_utils import database_exists

from api.api import GetDecksAttempted, GetScoreForDeck, GettingCard, PublicDecks, UserLoginAPI, UserOwnDeckCards, UserOwnDeckList, UserRegisterAPI
from api.database import db  # importing SQLAlchemy instance
from api.models import User
# for configuration of Flask App
from application.config import LocalDevelopmentConfig


def create_app():
    app = Flask(__name__)
    app.config.from_object(
        LocalDevelopmentConfig
    )  # setting the configuration of Flask App

    db.init_app(app)  # for database setup

    api = Api(app)  # Main entry point for the application (with api)

    api.app.config['RESTFUL_JSON'] = {
        'ensure_ascii': False
    }

    with app.app_context():
        if not database_exists(app.config["SQLALCHEMY_DATABASE_URI"]):
            db.create_all()
    # above code creates the database if it does not exist

    # creating and pushing context so that it can be used in other files
    app.app_context().push()

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(
            int(user_id)
        )  # used for maintaining the current user of the app

    from application.controllers.auth_controllers import auth as auth_blueprint
    from application.controllers.main_controllers import main_cont as main_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)

    return app, api


app, api = create_app()

api.add_resource(UserLoginAPI, "/api/user/login", "/api/user/<int:user_id>")
api.add_resource(UserRegisterAPI, "/api/user/register")

api.add_resource(
    UserOwnDeckList, "/api/decks/update", "/api/decks/add", "/api/key=<string:api_key>/user_id=<int:user_id>/decks", "/api/key=<string:api_key>/user_id=<int:user_id>/delete/deck=<int:deck_id>")
api.add_resource(
    UserOwnDeckCards, "/api/deck/card/update", "/api/deck/cards/add", "/api/<string:api_key>/user=<int:user_id>/deck=<int:deck_id>/cards", "/api/<string:api_key>/user=<int:user_id>/delete/deck=<int:deck_id>/card=<int:card_id>")

api.add_resource(PublicDecks, "/api/decks/public")
api.add_resource(
    GettingCard, "/api/deck/study", "/api/<string:api_key>/user=<int:user_id>/deck_id=<int:deck_id>/card=<int:card_id>/study")

api.add_resource(GetScoreForDeck, "/hi/<string:api_key>/user=<int:user_id>/deck_id=<int:deck_id>/")
api.add_resource(GetDecksAttempted, "/hi/<string:api_key>/user=<int:user_id>/")

if __name__ == "__main__":
    app.run(port=8000)  # running the app at port 8000
