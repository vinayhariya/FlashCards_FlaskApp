from flask import Flask
from flask_restful import Api
from flask_login import LoginManager
from sqlalchemy_utils import database_exists

from api.api import *
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

api.add_resource(
    UserLoginAPI, "/api/user/user_id=<int:user_id>/get", "/api/user/login")

api.add_resource(UserRegisterAPI, "/api/user/register")

api.add_resource(
    UserDeckList, "/api/user_id=<int:user_id>/api_key=<string:api_key>/decksList")

api.add_resource(DeckResource,
                 "/api/user_id=<int:user_id>/api_key=<string:api_key>/deck_id=<int:deck_id>/get",
                 "/api/deck/add",
                 "/api/deck/update",
                 "/api/user_id=<int:user_id>/api_key=<string:api_key>/deck_id=<int:deck_id>/delete"
                 )

api.add_resource(
    DeckCardList, "/api/user_id=<int:user_id>/api_key=<string:api_key>/deck_id=<int:deck_id>/cardsList")

api.add_resource(CardResource,
                 "/api/user_id=<int:user_id>/api_key=<string:api_key>/card_id=<int:card_id>/get",
                 "/api/deck/card/add",
                 "/api/deck/card/update",
                 "/api/user_id=<int:user_id>/api_key=<string:api_key>/deck_id=<int:deck_id>/card_id=<int:card_id>/delete"
                 )

api.add_resource(
    PublicDecks, "/api/user_id=<int:user_id>/api_key=<string:api_key>/publicDecks")

api.add_resource(
    UserDeckScore, "/api/user_id=<int:user_id>/api_key=<string:api_key>/deck_id=<int:deck_id>/score/get")

api.add_resource(UserDeckAttempted,
                 "/api/user_id=<int:user_id>/api_key=<string:api_key>/decks_attempted/get")

api.add_resource(
    StudyCard, "/api/user_id=<int:user_id>/api_key=<string:api_key>/deck_id=<int:deck_id>/card_id=<int:card_id>/study/get", "/api/deck/study")

api.add_resource(PublicDeckAuthorRelated,
                 "/api/user_id=<int:user_id>/api_key=<string:api_key>/publicDecks/author=<string:author_name>/get")


if __name__ == "__main__":
    # running the app at port 8000
    # app.run(host="127.0.0.1", port=8000)  # if running on localhost

    app.run(host="0.0.0.0", port=8080) # if running on replit
