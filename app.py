#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime

#----------------------------------------------------------------------------#
class FlashType:
    ERROR = 'danger'
    SUCCESS = 'success'
    INFO = 'info'
    WARNING = 'warning'
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    #added:
    _genres = db.Column('genres', db.String(120))
    website = db.Column(db.String(120), nullable=True)
    seeking_talent = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(200), nullable=True)

    shows = db.relationship('Show', back_populates='venue')

    @property
    def genres(self):
      return json.loads(self._genres)

    @genres.setter
    def genres(self, value):
      self._genres = json.dumps(value)


    def __repr__(self):
      return f'<Venue: id: {self.id}, name: {self.name}>'

    def to_dict(self):
      return {
        x.name: getattr(self, x.name)
        for x in self.__table__.columns
      }

    def update_from_dict(self, data):
      for key, value in data.items():
        setattr(self, key, value)

    def num_upcoming_shows(self):
      return Show.query.filter(Show.start_time > datetime.now(),
                               Show.venue_id == self.id).count()

    def num_past_shows(self):
      return Show.query.filter(Show.start_time < datetime.now(),
                               Show.venue_id == self.id).count()

    def get_upcoming_shows(self):
      return Show.query.filter(Show.start_time > datetime.now(),
                               Show.venue_id == self.id).all()

    def get_past_shows(self):
      return Show.query.filter(Show.start_time < datetime.now(),
                               Show.venue_id == self.id).all()


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # added:
    _genres = db.Column('genres', db.String(120))
    website = db.Column(db.String(120), nullable=True)
    seeking_venue = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(200), nullable=True)

    #venues = db.relationship('Venue', secondary='Show', back_populates='artists')
    shows = db.relationship('Show', back_populates='artist')

    @property
    def genres(self):
      return json.loads(self._genres)

    @genres.setter
    def genres(self, value):
      self._genres = json.dumps(value)

    def __repr__(self):
      return f'<Artist: id: {self.id}, name: {self.name}>'

    def to_dict(self):
      return {
        x.name: getattr(self, x.name)
        for x in self.__table__.columns
      }

    def update_from_dict(self, data):
      for key, value in data.items():
        setattr(self, key, value)

    def num_upcoming_shows(self):
      return Show.query.filter(Show.start_time > datetime.now(),
                               Show.artist_id == self.id).count()

    def num_past_shows(self):
      return Show.query.filter(Show.start_time < datetime.now(),
                               Show.artist_id == self.id).count()

    def get_upcoming_shows(self):
      return Show.query.filter(Show.start_time > datetime.now(),
                               Show.artist_id == self.id).all()

    def get_past_shows(self):
      return Show.query.filter(Show.start_time < datetime.now(),
                               Show.artist_id == self.id).all()

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer(), db.ForeignKey('Venue.id'))
    artist_id = db.Column(db.Integer(), db.ForeignKey('Artist.id'))
    start_time = db.Column(db.DateTime(timezone=True))

    venue = db.relationship('Venue', back_populates='shows')
    artist = db.relationship('Artist', back_populates='shows')

    def __repr__(self):
      return f'<Show: venue_id: {self.venue_id}, artist_id: {self.artist_id}'

    def to_dict(self):
      return {
        x.name: getattr(self, x.name)
        for x in self.__table__.columns
      }

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Display form validation errors 
#----------------------------------------------------------------------------#
def flash_form_error_message(form):
  for field, errors in form.errors.items():
    err_list = ', '.join(errors)
    msg = f'{form[field].label.text}: {err_list}'
    flash(msg, FlashType.ERROR)

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues/')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

  areas = []
  cities = db.session.query(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
  for city in cities:
    area = {
      'city': city[0],
      'state': city[1],
      'venues': [
            {
              'id': x.id,
              'name': x.name,
              'num_upcoming_shows': x.num_upcoming_shows(),
            }
            for x in Venue.query.filter(Venue.city == city[0], Venue.state == city[1]).all()
        ]
    }
    #print(area)
    areas.append(area)

  return render_template('pages/venues.html', areas=areas)

@app.route('/venues/search/', methods=['POST'])
def search_venues():

  search_term = request.form.get('search_term', '')
  q = f'%{search_term}%'
  venues = Venue.query.filter(Venue.name.ilike(q)).all()

  response = {
       'count': len(venues),
       'data': [
            {
               'id': x.id,
               'name': x.name,
               'num_upcoming_shows': x.num_upcoming_shows()
            }
            for x in venues
         ],
    }

  #print(response)
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>/')
def show_venue(venue_id):

  venue = db.session.get(Venue, venue_id)
  if venue is None:
    abort(404)

  data = venue.to_dict()

  data['upcoming_shows'] = [
        {
          'artist_id': x.artist_id,
          'artist_name': x.artist.name,
          'artist_image_link': x.artist.image_link,
          'start_time': x.start_time.isoformat(),
        }
        for x in venue.get_upcoming_shows()
    ]

  data['past_shows'] = [
        {
          'artist_id': x.artist_id,
          'artist_name': x.artist.name,
          'artist_image_link': x.artist.image_link,
          'start_time': x.start_time.isoformat(),
        }
        for x in venue.get_past_shows()
    ]

  data['past_shows_count'] = venue.num_past_shows()
  data['upcoming_shows_count'] = venue.num_upcoming_shows()

  #print(data)
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create/', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  form = VenueForm(request.form)
  #print(form.data)
  
  if not form.validate():
    flash_form_error_message(form)
    return render_template('forms/new_venue.html', form=form)

  try:
    venue = Venue(**form.data)
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  if error:
    flash(f'An error occurred. Venue {request.form["name"]} could not be listed.', FlashType.ERROR)
    abort(500)
  else:
    flash(f'Venue {request.form["name"]} was successfully listed!', FlashType.INFO)
    return redirect(url_for('index'))

@app.route('/venues/<venue_id>/delete/', methods=['POST'])
def delete_venue(venue_id):

  error = False
  venue = db.session.get(Venue, venue_id)
  if venue is None:
    abort(404)

  try:
    db.session.delete(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  if error:
    flash(f'An error occurred. Venue {venue.name} could not be deleted.', FlashType.ERROR)
    abort(500)
  else:
    flash(f'Venue {venue.name} was deleted!', FlashType.INFO)
    return redirect(url_for('index'))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists/')
def artists():

  data = [
        {
            'id': x.id,
            'name': x.name,
        }
        for x in Artist.query.all()
    ]

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search/', methods=['POST'])
def search_artists():

  search_term = request.form.get('search_term', '')
  q = f'%{search_term}%'
  artists = Artist.query.filter(Artist.name.ilike(q)).all()

  response = {
       'count': len(artists),
       'data': [
            {
               'id': x.id,
               'name': x.name,
               'num_upcoming_shows': x.num_upcoming_shows()
            }
            for x in artists
         ],
    }

  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>/')
def show_artist(artist_id):

  artist = db.session.get(Artist, artist_id)
  if artist is None:
    abort(404)

  data = artist.to_dict()

  data['upcoming_shows'] = [
        {
            'venue_id': x.venue_id,
            'venue_name': x.venue.name,
            'venue_image_link': x.venue.image_link,
            'start_time': x.start_time.isoformat(),
        }
        for x in artist.get_upcoming_shows()
    ]

  data['past_shows'] = [
        {
            'venue_id': x.venue_id,
            'venue_name': x.venue.name,
            'venue_image_link': x.venue.image_link,
            'start_time': x.start_time.isoformat(),
        }
        for x in artist.get_past_shows()
    ]

  data['upcoming_shows_count'] = artist.num_upcoming_shows()
  data['past_shows_count'] = artist.num_past_shows()

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit/', methods=['GET'])
def edit_artist(artist_id):

  artist = db.session.get(Artist, artist_id)
  if artist is None:
    abort(404)

  data = artist.to_dict()
  form = ArtistForm()
  form.genres.default = data['genres']
  form.process(**data)

  return render_template('forms/edit_artist.html', form=form, artist=data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  error = False
  artist = db.session.get(Artist, artist_id)
  if artist is None:
    abort(404)

  form = ArtistForm(request.form)
  #print(form.data)

  if not form.validate():
    flash_form_error_message(form)
    data = artist.to_dict()
    return render_template('forms/edit_artist.html', form=form, artist=data)

  try:
    artist.update_from_dict(form.data)
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  if error:
    flash(f'An error occurred. Artist {request.form["name"]} could not be updated.', FlashType.ERROR)
    abort(500)    
  else:
    flash(f'Artist {request.form["name"]} was successfully updated!', FlashType.INFO)  
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit/', methods=['GET'])
def edit_venue(venue_id):

  venue = db.session.get(Venue, venue_id)
  if venue is None:
    abort(404)

  data = venue.to_dict()
  #print(data)
  form = VenueForm()
  form.genres.default = data['genres']
  form.process(**data)

  return render_template('forms/edit_venue.html', form=form, venue=data)

@app.route('/venues/<int:venue_id>/edit/', methods=['POST'])
def edit_venue_submission(venue_id):

  error = False
  venue = db.session.get(Venue, venue_id)
  if venue is None:
    abort(404)

  form = VenueForm(request.form)
  if not form.validate():
    flash_form_error_message(form)
    data = venue.to_dict()
    return render_template('forms/edit_venue.html', form=form, venue=data)

  try:
    venue.update_from_dict(form.data)
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  
  if error:
    flash(f'An error occured. Venue {request.form["name"]} could not be updated!', FlashType.ERROR)
    abort(500)
  else:
    flash(f'Venue {request.form["name"]} was successfully updated!', FlashType.INFO)
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create/', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

    error = False
    form = ArtistForm(request.form)
    #print(form.data)
    if not form.validate():
      flash_form_error_message(form)
      return render_template('forms/new_artist.html', form=form)      

    try:
      artist = Artist(**form.data)
      db.session.add(artist)
      db.session.commit()
    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
  
    if error:
      flash('An error occurred. Artist {request.form["name"]} could not be listed.', FlashType.ERROR)
      abort(500)
    else:
      flash(f'Artist {request.form["name"]} was successfully listed!', FlashType.INFO)
      return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows/')
def shows():

  data = [
        {
          'venue_id': x.venue_id,
          'venue_name': x.venue.name,
          'artist_id': x.artist_id,
          'artist_name': x.artist.name,
          'artist_image_link': x.artist.image_link,
          'start_time': x.start_time.isoformat()
        }
        for x in Show.query.all()
    ]

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create/')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  error = False
  form = ShowForm(request.form)

  if not form.validate():
    flash_form_error_message(form)
    return render_template('forms/new_show.html', form=form)

  try:
    show = Show(**form.data)
    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  if error:
    flash('An error occured. The new show could not be listed!')
    abort(500)
  else:
    flash('Show was successfully listed!')
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
