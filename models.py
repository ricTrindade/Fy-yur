import os
from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate
from config import SQLALCHEMY_DATABASE_URI
from flask_wtf import Form
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ARRAY

# App & DB Config
app = Flask(__name__)
app.secret_key = os.urandom(24)
moment = Moment(app)
load_dotenv()
DATABASE_URL = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Association Table
show = db.Table('show',
    db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'), nullable=False, primary_key=True),
    db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id'), nullable=False, primary_key=True),
    db.Column('start_time', db.DateTime, nullable=False, primary_key=True)
)

# Venue Model
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    genres = db.Column(ARRAY(db.String), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(500), nullable=False)
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(120), nullable=True)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    artists = db.relationship('Artist', secondary=show, backref=db.backref('venues', lazy=True))

# Artist Model
class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(ARRAY(db.String), nullable=True)
    website = db.Column(db.String(500), nullable=True)
    seeking_venue = db.Column(db.Boolean, nullable=True, default=False)
    seeking_description = db.Column(db.String(120), nullable=True)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))