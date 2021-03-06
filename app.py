#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app,db)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://postgres:root@localhost:5432/fyyur"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'
    __searchable__= ["name","city","state","address"]
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120),nullable=False)
    address = db.Column(db.String(120),nullable=False)
    phone = db.Column(db.String(120),nullable=False)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_description = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    website = db.Column(db.String())
    shows_ven = db.relationship('Show', backref='venue')
    past_shows_count = db.Column(db.Integer)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'
    __searchable__= ["name","city","state"]
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120),nullable=False )  
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String())
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(200))
    website = db.Column(db.String())
    shows_art = db.relationship("Show", backref="artist")

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
  __tablename__='show'
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), primary_key=True)
  start_time = db.Column(db.String(), nullable=False)
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[]
  venues = Venue.query.all()

  for venue in venues:

    
    data.append({
      "city" : venue.city ,
      "state" : venue.state ,
      "venues" : [{
        "id" : venue.id,
        "name" : venue.name 
      }]
    })
    
  
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  data = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term))).all()
  count = []
  for outcome in data:
    count.append({
      "id":outcome.id,
      "name": outcome.name
    })
  response = {
    "count":len(data),
    "data": count
  }
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  selected_venue=Venue.query.get(venue_id)
  past_shows =[]
  upcoming_shows = []
  shows=Show.query.filter_by(venue_id=venue_id).all()

  for show in shows:

    if show.start_time < str(datetime.now()):

     past_shows.append({
     "artist_id": show.artist_id,
     "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
     "artist_image_link":Venue.query.filter_by(id=show.venue_id).first().image_link ,
     "start_time": str(show.start_time) })
    else:
      upcoming_shows.append({
      "artist_id": show.artist_id,
      "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
      "artist_image_link":Venue.query.filter_by(id=show.venue_id).first().image_link ,
      "start_time": show.start_time })
  
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = {
    "id": selected_venue.id,
    "name": selected_venue.name,
    "genres": selected_venue.genres ,
    "address": selected_venue.address,
    "city": selected_venue.city,
    "state": selected_venue.state,
    "phone": selected_venue.phone,
    "website": selected_venue.website,
    "facebook_link": selected_venue.facebook_link,
    "seeking_talent": True,
    "seeking_description": selected_venue.seeking_description,
    "image_link":selected_venue.image_link ,
    "past_shows":past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm()
  try:
   added_venue=Venue(
    name=form.name.data,
    genres=form.genres.data,
    city=form.city.data,
    state=form.state.data,
    phone=form.phone.data,
    address= form.address.data,
    facebook_link=form.facebook_link.data,
    image_link=form.image_link.data
    )
   db.session.add(added_venue)
   db.session.commit()

  # on successful db insert, flash success
   flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    # TODO: on unsuccessful db insert, flash an error instead.
   db.session.rollback()
   flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
     db.session.close()
     return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  
  try:
    Show.query.filter(Show.venue_id==venue_id).delete()
    Venue.query.filter(Venue.id == venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return render_template('pages/home.html')

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
   #insert a button and send ajax call from main.html to this decorator

  return render_template('pages/venues.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  data=[]
  artists = Artist.query.all()

  for artist in artists:
      artist = dict(zip(('id', 'name'),(artist.id , artist.name)))
      data.append(artist)
  
    
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  data = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term))).all()
  info = []
  for outcome in data:
    info.append({
      "id":outcome.id,
      "name": outcome.name
    })
  response = {
    "count":len(data),
    "data": info
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  selected_artist= Artist.query.get(artist_id)
  past_shows =[]
  upcoming_shows = []
  shows=Show.query.filter_by(artist_id=artist_id).all()

  for show in shows:

    if show.start_time < str(datetime.now()):

     past_shows.append({
     "venue_id": show.venue_id,
     "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
     "venue_image_link":Venue.query.filter_by(id=show.venue_id).first().image_link ,
     "start_time": str(show.start_time) })
    else:
      upcoming_shows.append({
      "venue_id": show.venue_id,
      "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
      "venue_image_link":Venue.query.filter_by(id=show.venue_id).first().image_link ,
      "start_time": str(show.start_time) })
      
 
  data={
    "id": selected_artist.id,
    "name": selected_artist.name,
    "genres": selected_artist.genres,
    "city": selected_artist.city,
    "state": selected_artist.state,
    "phone": selected_artist.phone,
    "website": selected_artist.website,
    "facebook_link": selected_artist.facebook_link,
    "seeking_venue": True,
    "seeking_description": selected_artist.seeking_description,
    "image_link": selected_artist.image_link,
    "past_shows":past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
 
  # TODO: populate form with fields from artist with ID <artist_id>
  selected_artist= Artist.query.get(artist_id)
  form.name.data = selected_artist.name
  form.genres.data=selected_artist.genres,
  form.city.data = selected_artist.city,
  form.state.data = selected_artist.state,
  form.phone.data = selected_artist.phone,
  form.facebook_link.data = selected_artist.facebook_link,
  #form.image_link.data = edit_artist.image_link
  artist={
    "id": selected_artist.id,
    "name": selected_artist.name,
    "genres": selected_artist.genres,
    "city": selected_artist.city,
    "state": selected_artist.state,
    "phone": selected_artist.phone,
    "website": selected_artist.website,
    "facebook_link": selected_artist.facebook_link,
    "seeking_venue": True,
    "seeking_description": selected_artist.seeking_description,
    "image_link": selected_artist.image_link,
    "past_shows": [{
      "venue_id": "",
      "venue_name": "",
      "venue_image_link": "",
      "start_time": ""
    }],
    "upcoming_shows": [],
    #"past_shows_count": selected_artist.past_shows_count,
    "upcoming_shows_count": 0,
  }
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm()
  try:
    
    edited_artist=Artist.query.get(artist_id)
    edited_artist.name=form.name.data,
    edited_artist.genres=form.genres.data,
    edited_artist.city=form.city.data,
    edited_artist.state=form.state.data,
    edited_artist.phone=form.phone.data,
    edited_artist.facebook_link=form.facebook_link.data,
    edited_artist.image_link=form.image_link.data
    
   #db.session.add(edited_artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  except:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
     db.session.rollback()
     flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  finally:
     db.session.close()
     return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm()
  try:
   added_artist=Artist(
    name=form.name.data,
    genres=form.genres.data,
    city=form.city.data,
    state=form.state.data,
    phone=form.phone.data,
    facebook_link=form.facebook_link.data,
    image_link=form.image_link.data
    )
   db.session.add(added_artist)
   db.session.commit()
    # on successful db insert, flash success
   flash('Artist ' + request.form['name'] + ' was successfully listed!')

  except:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
     db.session.rollback()
     flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  finally:
     db.session.close()
     return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  data=[]
  shows = Show.query.all()

  for show in shows:

    
    data.append({
    "venue_id": show.venue_id,
    "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
    "artist_id": show.artist_id,
    "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
    "artist_image_link":Artist.query.filter_by(id=show.artist_id).first().image_link ,
    "start_time": show.start_time })
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm()
  try:
   added_show=Show(
    artist_id=form.artist_id.data,
    venue_id=form.venue_id.data,
    start_time=form.start_time.data,
    )
   db.session.add(added_show)
   db.session.commit()
   # on successful db insert, flash success
   flash('Show was successfully listed!')
  except:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    db.session.rollback()
    flash('An error occurred. show could not be listed.')
  finally:
     db.session.close()
     return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
