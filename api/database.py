# from sqlalchemy.ext.declarative import declarative_base
# Base = declarative_base()
# engine = None

import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

base_dir = os.path.abspath(os.path.dirname(__file__))
parent_dir = os.path.abspath(os.path.join(base_dir, os.pardir))
SQLITE_DB_DIR = os.path.join(parent_dir, "api\\db_directory")
SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(SQLITE_DB_DIR, "flash_db.sqlite3")
