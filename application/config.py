import os
from api.database import SQLITE_DB_DIR, SQLALCHEMY_DATABASE_URI

base_dir = os.path.abspath(os.path.dirname(__file__))
parent_dir = os.path.abspath(os.path.join(base_dir, os.pardir))


"""
class Config:
    DEBUG = True
    SQLITE_DB_DIR = None
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    pass
"""
# above copied from Week 6 screencast (TODO remove in final submimssion)

# class LocalDevelopmentConfig(Config):
class LocalDevelopmentConfig:  # used for configuration of Flask app

    SQLITE_DB_DIR = SQLITE_DB_DIR
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    STATIC_FOLDER = os.path.join(parent_dir, "application\\static")
    # TEMPLATE_FOLDER = os.path.join(parent_dir, "application\\templates")
    DEBUG = True
    SECRET_KEY = "secretkeyishere"
