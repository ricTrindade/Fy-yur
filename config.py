import os
SECRET_KEY = os.urandom(32)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# The DB is hosted on a AIVEN Service - The DB URI contains sensitive data
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

# App & DB Config
app = Flask(__name__)
app.secret_key = os.urandom(24)
moment = Moment(app)
load_dotenv()
DATABASE_URL = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
db = SQLAlchemy(app)
migrate = Migrate(app, db)
