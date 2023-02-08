import json
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

#----------------------------------------------------------------------------#
# SQLAlchemy instance
#----------------------------------------------------------------------------#
db = SQLAlchemy()

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
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    website = db.Column(db.String(120), nullable=True)
    seeking_talent = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now())

    shows = db.relationship(
        'Show', 
        back_populates='venue',
        order_by='Show.start_time',
        lazy='joined', 
        cascade='all,delete-orphan'
      )

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
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    website = db.Column(db.String(120), nullable=True)
    seeking_venue = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now())

    shows = db.relationship(
        'Show', 
        back_populates='artist', 
        order_by='Show.start_time',
        lazy='joined', 
        cascade='all,delete-orphan'
      )

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
