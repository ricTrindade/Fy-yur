import json
import sys

import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import select, ARRAY

from forms import *
import os
from dotenv import load_dotenv
from flask_migrate import Migrate

# App & DB Config
app = Flask(__name__)
app.secret_key = os.urandom(24)
moment = Moment(app) # TODO: Investigate what this is!
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Association Table
show = db.Table('show',
    db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'), primary_key=True),
    db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id'), primary_key=True),
    db.Column('start_time', db.DateTime, nullable=False)
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

# Filters.
def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime # TODO: I am not sure what this is

# Home page Controller
@app.route('/')
def index():
  return render_template('pages/home.html')

#  Venues page Controller
@app.route('/venues')
def venues():
  # Query table to get venues
  venues_in_db = Venue.query.order_by('id').all()
  data = []

  # Create a dictionary to group venues by (city, state)
  grouped_venues = {}

  for venue in venues_in_db:
    venue_data = {
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows":  0 #TODO:len([show for show in venue.shows if show.start_time > datetime.now()])
    }

    # Group venues by city and state
    key = (venue.city, venue.state)
    if key not in grouped_venues:
      grouped_venues[key] = []
    grouped_venues[key].append(venue_data)

  # Build the final data structure
  for (city, state), venues_var in grouped_venues.items():
    data.append({
      "city": city,
      "state": state,
      "venues": venues_var
    })

  return render_template('pages/venues.html', areas=data)

# Search Through Venues
@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term=request.form.get('search_term', '')

  # Query venues with case-insensitive partial match
  venues_in_db = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all()

  # Build the response with the count and matched venues
  response = {
    "count": len(venues_in_db),
    "data": []
  }

  for venue in venues_in_db:
    # Count upcoming shows
    num_upcoming_shows = db.session.query(show).filter(
      show.c.venue_id == venue.id,
      show.c.start_time > datetime.now()
    ).count()

    response["data"].append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": num_upcoming_shows
    })

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

# Get Venues by ID
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  venues_in_db = Venue.query.order_by('id').all()
  data = []

  for venue in venues_in_db:
    past_shows = []
    upcoming_shows = []

    # Iterate over all artists associated with the venue through the 'shows' association table
    for artist in venue.artists:
      # Find the corresponding show details
      show_rel = db.session.query(show).filter_by(venue_id=venue.id, artist_id=artist.id).first()

      if show_rel:
        show_data = {
          "artist_id": artist.id,
          "artist_name": artist.name,
          "artist_image_link": artist.image_link,
          "start_time": format_datetime(str(show_rel.start_time))
        }

        # Categorize show as past or upcoming based on current date
        if show_rel.start_time < datetime.now():
          past_shows.append(show_data)
        else:
          upcoming_shows.append(show_data)

    # Create venue data dictionary
    venue_data = {
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres,
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows),
    }

    data.append(venue_data)

  data = list(filter(lambda d: d['id'] == venue_id, data))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue #
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  with app.app_context():
    try:
      # Get Data from JSON
      name = request.form['name']
      city = request.form['city']
      state = request.form['state']
      address = request.form['address']
      phone = request.form['phone']
      genres = request.form.getlist('genres')
      website = request.form['website_link']
      seeking_talent = True if request.form.get('seeking_talent') == 'on' else False
      seeking_description = request.form['seeking_description']
      image_link = request.form['image_link']
      facebook_link = request.form['facebook_link']

      # Create artist
      venue = Venue(
        name=name,
        city=city,
        state=state,
        address = address,
        phone=phone,
        genres=genres,
        website=website,
        seeking_talent=seeking_talent,
        seeking_description=seeking_description,
        image_link=image_link,
        facebook_link=facebook_link
      )

      # Add artist to the database
      db.session.add(venue)
      db.session.commit()
    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()

  if not error:
    flash('Venue successfully listed!')
  else:
    flash('An error occurred. Venue could not be listed.')
  return redirect(url_for('index'))

# Delete Venues by ID
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

# Get Artists
@app.route('/artists')
def artists():

  # Query Table to Get Artists
  artists_in_db = Artist.query.order_by('id').all()
  data=[]

  for artist in artists_in_db:
    artist_id = artist.id
    artist_name = artist.name
    artist_data = {"id" : artist_id, "name" : artist_name}
    data.append(artist_data)

  return render_template('pages/artists.html', artists=data)

# Search Through Artists
@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')

  # Query artists with case-insensitive partial match
  artist_in_db = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).all()

  # Build the response with the count and matched venues
  response = {
    "count": len(artist_in_db),
    "data": []
  }

  for artist in artist_in_db:
    # Count upcoming shows
    num_upcoming_shows = db.session.query(show).filter(
      show.c.artist_id == artist.id,
      show.c.start_time > datetime.now()
    ).count()

    response["data"].append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": num_upcoming_shows
    })

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

# Get artist by ID
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  artists_in_db = Artist.query.order_by('id').all()
  data = []

  for artist in artists_in_db:
    past_shows = []
    upcoming_shows = []

    for venue in artist.venues:
      show_rel = db.session.query(show).filter_by(venue_id=venue.id, artist_id=artist.id).first()

      if show_rel:
        show_data = {
          "venue_id": venue.id,
          "venue_name": venue.name,
          "venue_image_link": venue.image_link,
          "start_time": format_datetime(str(show_rel.start_time))
        }

        # Categorize show as past or upcoming based on current date
        if show_rel.start_time < datetime.now():
          past_shows.append(show_data)
        else:
          upcoming_shows.append(show_data)

    artist_data = {
      "id" : artist.id,
      "name" : artist.name,
      "genres" : artist.genres,
      "city" : artist.city,
      "state" : artist.state,
      "phone" : artist.phone,
      "website" : artist.website,
      "facebook_link" : artist.facebook_link,
      "seeking_venue" : artist.seeking_venue,
      "seeking_description" : artist.seeking_description,
      "image_link" : artist.image_link,
      "past_shows" : past_shows,
      "upcoming_shows" : upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count":len(upcoming_shows)
    }

    data.append(artist_data)

  data = list(filter(lambda d: d['id'] == artist_id, data))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update artist Info
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get_or_404(artist_id)
  form = ArtistForm(obj=artist)

  # Pass artist details as a dictionary for rendering the template
  artist_data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist_data)

#  Update artist Info
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try:
    # Retrieve data from the form
    new_name = request.form['name']
    new_city = request.form['city']
    new_state = request.form['state']
    new_phone = request.form['phone']
    new_genre = request.form.getlist('genres')
    new_facebook_link = request.form['facebook_link']
    new_image_link = request.form['image_link']
    new_website = request.form['website_link']
    new_seeking_venue = True if request.form.get('seeking_venue') == 'y' else False
    new_seeking_description = request.form['seeking_description']

    # Get Artist
    artist = Artist.query.get(artist_id)

    # Update artist info
    artist.name = new_name
    artist.city = new_city
    artist.state = new_state
    artist.phone = new_phone
    artist.genre = new_genre
    artist.facebook_link = new_facebook_link
    artist.image_link = new_image_link
    artist.website = new_website
    artist.seeking_venue = new_seeking_venue
    artist.seeking_description = new_seeking_description

    db.session.commit()
    flash('Artist Info Was Updated')

  except Exception as e:
    db.session.rollback()
    flash('An error occurred. Artist could not be updated.')
    print(f"Error: {e}")

  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

# Edit venue Info
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get_or_404(venue_id)
  form = VenueForm(obj=venue)

  # Pass artist details as a dictionary for rendering the template
  venue_data = {
    "id": venue.id,
    "name": venue.name,
    "address" : venue.address,
    "genres": venue.genres,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue_data)

# Edit venue Info
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try:
    # Retrieve data from the form
    new_name = request.form['name']
    new_city = request.form['city']
    new_state = request.form['state']
    new_address = request.form['address']
    new_phone = request.form['phone']
    new_genre = request.form.getlist('genres')
    new_facebook_link = request.form['facebook_link']
    new_image_link = request.form['image_link']
    new_website = request.form['website_link']
    new_seeking_talent = True if request.form.get('seeking_talent') == 'y' else False
    new_seeking_description = request.form['seeking_description']

    # Get Artist
    venue = Venue.query.get(venue_id)

    # Update artist info
    venue.name = new_name
    venue.city = new_city
    venue.state = new_state
    venue.phone = new_phone
    venue.genre = new_genre
    venue.facebook_link = new_facebook_link
    venue.image_link = new_image_link
    venue.website = new_website
    venue.seeking_venue = new_seeking_talent
    venue.seeking_description = new_seeking_description

    db.session.commit()
    flash('Venue Info Was Updated')

  except Exception as e:
    db.session.rollback()
    flash('An error occurred. Venue could not be updated.')
    print(f"Error: {e}")

  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

#  Create Artist
@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

  error = False
  with app.app_context():
    try:
      # Get Data from JSON
      name = request.form['name']
      city = request.form['city']
      state = request.form['state']
      phone = request.form['phone']
      genres = request.form.getlist('genres')
      website = request.form['website_link']
      seeking_venue = True if request.form.get('seeking_venue') == 'on' else False
      seeking_description = request.form['seeking_description']
      image_link = request.form['image_link']
      facebook_link = request.form['facebook_link']

      # Create artist
      artist = Artist(
        name = name,
        city = city,
        state = state,
        phone = phone,
        genres = genres,
        website = website,
        seeking_venue = seeking_venue,
        seeking_description = seeking_description,
        image_link = image_link,
        facebook_link = facebook_link
      )

      # Add artist to the database
      db.session.add(artist)
      db.session.commit()
    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()

  if not error:
    flash('Artist successfully listed!')
  else:
    flash('An error occurred. Artist could not be listed.')
  return redirect(url_for('index'))

#  GET ALL Shows
@app.route('/shows')
def shows():
  # displays list of shows at /shows
  shows_in_db = db.session.execute(select(show)).fetchall()
  data = []

  for event in shows_in_db:
    venue = Venue.query.get(event.venue_id)
    venue_id = venue.id
    venue_name = venue.name
    artist = Artist.query.get(event.artist_id)
    artist_id = artist.id
    artist_name = artist.name
    artist_image_link = artist.image_link
    start_time = event.start_time
    event_data = {
      "venue_id": venue_id,
      "venue_name": venue_name,
      "artist_id": artist_id,
      "artist_name":artist_name,
      "artist_image_link": artist_image_link,
      "start_time": format_datetime(str(start_time))
    }
    data.append(event_data)

  return render_template('pages/shows.html', shows=data)

# Create Shows
@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

# Create all Shows
@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  try:
    # Retrieve data from the form
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']

    # Insert into the association table
    insert_stmt = show.insert().values(
      artist_id=artist_id,
      venue_id=venue_id,
      start_time=format_datetime(str(start_time))
    )
    db.session.execute(insert_stmt)
    db.session.commit()
    flash('Show was successfully listed!')

  except Exception as e:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
    print(f"Error: {e}")

  finally:
    db.session.close()

  return redirect(url_for('index'))

# Log Errors when Needed
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

# Log Errors when Needed
@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

# Log Errors when Needed
if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
