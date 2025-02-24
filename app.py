import os
import sys

import dateutil.parser
import babel
from flask import render_template, request, flash, redirect, url_for
import logging
from logging import Formatter, FileHandler
from sqlalchemy import select
from models import app, show, Venue, Artist, db
from forms import *

# Filters.
def format_datetime(value, format_='medium'):
  date = dateutil.parser.parse(value)
  if format_ == 'full':
      format_= "EEEE MMMM, d, y 'at' h:mma"
  elif format_ == 'medium':
      format_= "EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format_, locale='en')

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

  # Create data to send to Front-End
  for venue in venues_in_db:

    # Get all upcoming shows
    num_upcoming_shows = db.session.query(show).filter(
      show.c.venue_id == venue.id,
      show.c.start_time > datetime.now()
    ).count()

    venue_data = {
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": num_upcoming_shows
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

  # Send data to Front End
  return render_template('pages/venues.html', areas=data)

# Search Through Venues
@app.route('/venues/search', methods=['POST']) 
def search_venues():

  # Fetch search term from front end
  search_term=request.form.get('search_term', '')

  # Query venues with case-insensitive partial match
  venues_in_db = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all()

  # Build the response with the count and matched venues
  response = {
    "count": len(venues_in_db),
    "data": []
  }

  # Create data to send to Front-End
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

  # Send to Front-End
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

# Get Venues by ID
@app.route('/venues/<int:venue_id>') 
def show_venue(venue_id):
  
  # shows the venue page with the given venue_id
  venues_in_db = Venue.query.order_by('id').all()
  data = []

  # Create data to send to Front End
  for venue in venues_in_db:
    past_shows = []
    upcoming_shows = []

    # Iterate over all artists associated with the venue
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

        # Categorise show as past or upcoming based on current date
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

#  Create Venue
@app.route('/venues/create', methods=['GET']) 
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

#  Create Venue
@app.route('/venues/create', methods=['POST']) 
def create_venue_submission():

  try:
    # Get Data from Front End
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    website = request.form['website_link']
    seeking_talent = True if request.form.get('seeking_talent') == 'y' else False
    seeking_description = request.form['seeking_description']
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']

    # Create new Venue
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

    # Add Venue to the database
    db.session.add(venue)
    db.session.commit()
    flash('Venue successfully listed!')

  except:
    db.session.rollback()
    flash('An error occurred. Venue could not be listed.')
    print(sys.exc_info())

  finally:
    db.session.close()

  return redirect(url_for('index'))

# Delete Venues by ID
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    # Find the venue by ID
    venue = Venue.query.get(venue_id)

    if not venue:
      flash(f"Venue with ID {venue_id} not found.", "error")
      return redirect(url_for('index'))  # Redirect to homepage if venue not found

    # Delete the venue
    db.session.delete(venue)
    db.session.commit()
    flash(f"Venue '{venue.name}' was successfully deleted!", "success")

  except Exception as e:
    db.session.rollback()
    flash(f"An error occurred while deleting the venue: {str(e)}", "error")
  finally:
    db.session.close()

    # Redirect to homepage after deletion
  return redirect(url_for('index'))

# Get Artists
@app.route('/artists') 
def artists():

  # Query Table to Get Artists
  artists_in_db = Artist.query.order_by('id').all()
  data=[]

  # Create data for front end
  for artist in artists_in_db:
    artist_id = artist.id
    artist_name = artist.name
    artist_data = {"id" : artist_id, "name" : artist_name}
    data.append(artist_data)

  # Send data to front end
  return render_template('pages/artists.html', artists=data)

# Search Through Artists
@app.route('/artists/search', methods=['POST']) 
def search_artists():

  # Fetch search term from front end
  search_term = request.form.get('search_term', '')

  # Query artists with case-insensitive partial match
  artist_in_db = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).all()

  # Build the response with the count and matched venues
  response = {
    "count": len(artist_in_db),
    "data": []
  }

  # Create data to send to front end
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

  # Send Data to front end
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

# Get artist by ID
@app.route('/artists/<int:artist_id>') 
def show_artist(artist_id):

  # Query table to get artists
  artists_in_db = Artist.query.order_by('id').all()
  data = []

  # Build data to send to front end
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

  # Send data to front end
  data = list(filter(lambda d: d['id'] == artist_id, data))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update artist Info
@app.route('/artists/<int:artist_id>/edit', methods=['GET']) 
def edit_artist(artist_id):

  # Fetch Artists from DB
  artist = Artist.query.get(artist_id)
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

    # Get Artist and Update Info
    artist = Artist.query.get(artist_id)
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

    # commit those changes to DB
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

  # Fetch Venue From DB
  venue = Venue.query.get(venue_id)
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

    # Get Venue and update Info
    venue = Venue.query.get(venue_id)
    venue.name = new_name
    venue.city = new_city
    venue.address = new_address
    venue.state = new_state
    venue.phone = new_phone
    venue.genre = new_genre
    venue.facebook_link = new_facebook_link
    venue.image_link = new_image_link
    venue.website = new_website
    venue.seeking_venue = new_seeking_talent
    venue.seeking_description = new_seeking_description

    # commit those changes to DB
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
  try:
    # Get Data from the form
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    website = request.form['website_link']
    seeking_venue = True if request.form.get('seeking_venue') == 'y' else False
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
    flash('Artist successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Artist could not be listed.')
  finally:
    db.session.close()

  return redirect(url_for('index'))

#  GET ALL Shows
@app.route('/shows') 
def shows():

  # displays list of shows at /shows
  shows_in_db = db.session.execute(select(show)).fetchall()
  data = []

  # Create data to send to front end
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

  # Send data to front end
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


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
