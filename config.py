import os
SECRET_KEY = os.urandom(32)

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# The DB is hosted on a AIVEN Service - The DB URI contains sensitive data
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
