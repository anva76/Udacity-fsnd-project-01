#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort, jsonify
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime, timezone
from models import Venue, Artist, Show, db

#----------------------------------------------------------------------------#
class FlashType:
    ERROR = 'danger'
    SUCCESS = 'success'
    INFO = 'info'
    WARNING = 'warning'

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

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
  venues = Venue.query.order_by(Venue.created_at.desc()).limit(10).all()
  artists = Artist.query.order_by(Artist.created_at.desc()).limit(10).all()
  return render_template('pages/home.html', venues=venues, artists=artists)

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues/')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

  areas = []
  cities = db.session.query(Venue.city, Venue.state).group_by(Venue.city, Venue.state)\
                                                    .order_by(Venue.city).all()  
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
            for x in Venue.query.filter(Venue.city == city[0], Venue.state == city[1])\
                                .order_by(Venue.name).all()
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

#  Advanced venue search
#  ----------------------------------------------------------------
@app.route('/venues/search_adv', methods=['GET', 'POST'])
def search_venues_advanced():

  if request.method == 'GET':
    form = SearchForm()
    return render_template('pages/search_venues_adv.html', results=None, form=form)

  form = SearchForm(request.form)
  name = form.data.get('name', '')
  city = form.data.get('city', '')
  state = form.data.get('state', '')
 
  if state != '':
    venues = Venue.query.filter(Venue.name.ilike(f'%{name}%'),
                                Venue.city.ilike(f'%{city}%'),
                                Venue.state == state).all()
  else:
    venues = Venue.query.filter(Venue.name.ilike(f'%{name}%'),
                                Venue.city.ilike(f'%{city}%')).all()     

  return render_template('pages/search_venues_adv.html', results=venues, form=form)


@app.route('/venues/<int:venue_id>/')
def show_venue(venue_id):

  venue = db.session.get(Venue, venue_id)
  if venue is None:
    abort(404)

  data = venue.to_dict()

  data['past_shows'] = []
  data['upcoming_shows'] = []

  for show in venue.shows:
    tmp_show = {
          'artist_id': show.artist_id,
          'artist_name': show.artist.name,
          'artist_image_link': show.artist.image_link,
          'start_time': show.start_time.isoformat(),       
      }
        
    if show.start_time <= datetime.now(timezone.utc):
      data['past_shows'].append(tmp_show)
    else:
      data['upcoming_shows'].append(tmp_show)     

  data['past_shows_count'] = len(data['past_shows'])
  data['upcoming_shows_count'] = len(data['upcoming_shows'])

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create/', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create/', methods=['POST'])
def create_venue_submission():
  error = False
  form = VenueForm(request.form)
  
  if not form.validate():
    flash_form_error_message(form)
    return render_template('forms/new_venue.html', form=form)

  try:
    venue = Venue()
    form.populate_obj(venue)
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


#  Delete Venue via an http post request
#  ----------------------------------------------------------------
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

#  Delete Venue via an http delete request (ajax) 
#  ----------------------------------------------------------------
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue_json(venue_id):
  error = False
  venue = db.session.get(Venue, venue_id)
  if venue is None:
    return jsonify ({
      'error': 'Venue was not found.'
    }), 404

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
    return jsonify({
      'error': f'Venue {venue.name} could not be deleted.'
    }), 500
  else:
    return jsonify({
      'venue': {
        'id': venue.id,
        'name': venue.name,
      }
    }), 201


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists/')
def artists():

  data = [
        {
            'id': x.id,
            'name': x.name,
        }
        for x in Artist.query.order_by(Artist.name).all()
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

#  Advanced artist search
#  ----------------------------------------------------------------
@app.route('/artists/search_adv', methods=['GET', 'POST'])
def search_artists_advanced():

  if request.method == 'GET':
    form = SearchForm()
    return render_template('pages/search_artists_adv.html', results=None, form=form)

  form = SearchForm(request.form)
  name = form.data.get('name', '')
  city = form.data.get('city', '')
  state = form.data.get('state', '')
 
  if state != '':
    artists = Artist.query.filter(Artist.name.ilike(f'%{name}%'),
                                 Artist.city.ilike(f'%{city}%'),
                                 Artist.state == state).all()
  else:
    artists = Artist.query.filter(Artist.name.ilike(f'%{name}%'),
                                 Artist.city.ilike(f'%{city}%')).all()     


  return render_template('pages/search_artists_adv.html', results=artists, form=form)


@app.route('/artists/<int:artist_id>/')
def show_artist(artist_id):

  artist = db.session.get(Artist, artist_id)
  if artist is None:
    abort(404)

  data = artist.to_dict()

  data['past_shows'] = []
  data['upcoming_shows'] = []
  for show in artist.shows:
    tmp_show = {
          'venue_id': show.venue_id,
          'venue_name': show.venue.name,
          'venue_image_link': show.venue.image_link,
          'start_time': show.start_time.isoformat(),        
      }

    if show.start_time <= datetime.now(timezone.utc):
      data['past_shows'].append(tmp_show)
    else:
      data['upcoming_shows'].append(tmp_show)

  data['upcoming_shows_count'] = len(data['upcoming_shows'])
  data['past_shows_count'] = len(data['past_shows'])

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit/', methods=['GET'])
def edit_artist(artist_id):

  artist = db.session.get(Artist, artist_id)
  if artist is None:
    abort(404)
  
  form = ArtistForm(obj=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit/', methods=['POST'])
def edit_artist_submission(artist_id):

  error = False
  artist = db.session.get(Artist, artist_id)
  if artist is None:
    abort(404)

  form = ArtistForm(request.form)

  if not form.validate():
    flash_form_error_message(form)
    return render_template('forms/edit_artist.html', form=form, artist=artist)

  try:
    form.populate_obj(artist)
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

  form = VenueForm(obj=venue)

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit/', methods=['POST'])
def edit_venue_submission(venue_id):

  error = False
  venue = db.session.get(Venue, venue_id)
  if venue is None:
    abort(404)

  form = VenueForm(request.form)
  if not form.validate():
    flash_form_error_message(form)
    return render_template('forms/edit_venue.html', form=form, venue=venue)

  try:
    form.populate_obj(venue)
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

@app.route('/artists/create/', methods=['POST'])
def create_artist_submission():

    error = False
    form = ArtistForm(request.form)

    if not form.validate():
      flash_form_error_message(form)
      return render_template('forms/new_artist.html', form=form)      

    try:
      artist = Artist()
      form.populate_obj(artist)
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
      return redirect(url_for('index'))

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
        for x in Show.query.order_by(Show.start_time).all()
    ]

  return render_template('pages/shows.html', shows=data)


# Create Show
# -----------------------------------------------------------
@app.route('/shows/create/', methods=['GET'])
def create_shows():
  artists = Artist.query.all()
  venues = Venue.query.all()
  form = ShowForm(artists=artists, venues=venues)

  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create/', methods=['POST'])
def create_show_submission():

  error = False
  artists = Artist.query.all()
  venues = Venue.query.all()
  form = ShowForm(request.form, artists=artists, venues=venues)

  if not form.validate():
    flash_form_error_message(form)
    return render_template('forms/new_show.html', form=form)

  try:
    show = Show()
    form.populate_obj(show)
    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  if error:
    flash('An error occured. The new show could not be listed!', FlashType.ERROR)
    abort(500)
  else:
    flash('Show was successfully listed!', FlashType.INFO)
    return redirect(url_for('index'))


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
