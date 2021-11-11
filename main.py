from flask import Flask
from flask_restful import Api
from application.config import LocalDevelopmentConfig
from api.database import db
from sqlalchemy_utils import database_exists


def create_app():
    app = Flask(__name__)
    app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)

    api = Api(app)
    app.app_context().push()

    with app.app_context():
        if not database_exists(app.config["SQLALCHEMY_DATABASE_URI"]):
            db.create_all()
        pass

    return app, api


app, api = create_app()

if __name__ == "__main__":
    app.run(port=8000)
