import json
from db import db
from datetime import datetime

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
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now())

    shows = db.relationship('Show', back_populates='venue', cascade='all,delete-orphan')

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
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now())

    shows = db.relationship('Show', back_populates='artist', cascade='all,delete-orphan')

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
