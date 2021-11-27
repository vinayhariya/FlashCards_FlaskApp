import os
from api.database import SQLITE_DB_DIR, SQLALCHEMY_DATABASE_URI

base_dir = os.path.abspath(os.path.dirname(__file__))
parent_dir = os.path.abspath(os.path.join(base_dir, os.pardir))

HOST = "http://127.0.0.1:8000" # uncomment if running on localhost
# HOST = "http://192.168.29.74:8080" # uncomment if running on replit (replace with the domain name)

class LocalDevelopmentConfig:  # used for configuration of Flask app

    SQLITE_DB_DIR = SQLITE_DB_DIR
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    STATIC_FOLDER = os.path.join(parent_dir, "application\\static")
    DEBUG = True
    SECRET_KEY = "secretkeyishere"
