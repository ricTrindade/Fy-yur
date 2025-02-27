from flask import Flask
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ARRAY

from config import Config

# App & DB Config
app = Flask(__name__)
app.config.from_object(Config)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Show Model
class Show(db.Model):

    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime,  nullable=False)

    # Relationships
    artist = db.relationship('Artist', back_populates='shows')
    venue = db.relationship('Venue', back_populates='shows')

    def __repr__(self):
        artist_name = Artist.query.get(self.artist_id).name
        venue_name = Venue.query.get(self.venue_id).name
        return f'<"Show:id({self.id}){artist_name}@{venue_name}, start_time={self.start_time}">'

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

    # Relationships
    shows = db.relationship('Show', back_populates='venue', lazy=True)

    def __repr__(self):
        return f'<"VENUE:id({self.id}){self.name}@{self.address},{self.city},{self.state}">'

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

    # Relationships
    shows = db.relationship('Show', back_populates='artist', lazy=True)

    def __repr__(self):
        return f'<"ARTIST:id({self.id}){self.name}@{self.city},{self.state}">'