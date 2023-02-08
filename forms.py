import re
from datetime import datetime
from flask_wtf import FlaskForm as Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, AnyOf, URL, optional, ValidationError
from enums import Genres, States

# Phone number validator
def valid_phone(form, field):
    regex = re.compile('^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$')

    if not regex.match(field.data):
        raise ValidationError('Invalid phone number.')

# State validator
def valid_state(form, field):
    if field.data not in States.validation_list():
        raise ValidationError('Invalid state.')

# Genres validator
def valid_genres(form, field):
    if not set(field.data).issubset(Genres.validation_list()):
        raise ValidationError('Invalid genres.')


class ShowForm(Form):
    def __init__(self, formdata=None, **kwargs):
        super().__init__(formdata, **kwargs)
        if 'venues' in kwargs:
                venue_choices = [(c.id, c.name) for c in kwargs['venues']]
                venue_choices.insert(0, ('',''))                
                self.venue_id.choices = venue_choices
        
        if 'artists' in kwargs:
                artist_choices = [(c.id, c.name) for c in kwargs['artists']]
                artist_choices.insert(0, ('',''))
                self.artist_id.choices = artist_choices

    artist_id = SelectField(
        'Artist',
        validators=[DataRequired()],
        choices=[]
    )
    venue_id = SelectField(
        'Venue',
        validators=[DataRequired()],
        choices=[]
    )
    start_time = DateTimeField(
            'Start Time', 
            validators=[DataRequired()], 
            default=datetime.today()
    )


class VenueForm(Form):
    name = StringField('Name', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state = SelectField(
            'State', 
            validators=[DataRequired(), valid_state],
            choices= States.choices()
    )
    address = StringField('Address', validators=[DataRequired()])
    phone = StringField('Phone', validators=[valid_phone,])
    image_link = StringField('Image link')
    genres = SelectMultipleField(
            'Genres', 
            validators=[DataRequired(), valid_genres],
            choices=Genres.choices()
    )
    facebook_link = StringField(
            'Facebook link', 
            validators=[URL(), optional()]
    )
    website = StringField(
            'Website', 
            validators=[URL(), optional()]
    )
    seeking_talent = BooleanField( 'Seeking talent' )
    seeking_description = StringField('Seeking description')


class ArtistForm(Form):
    name = StringField('Name', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state = SelectField(
            'State', 
            validators=[DataRequired(), valid_state],
            choices=States.choices()
    )
    phone = StringField('Phone', validators=[valid_phone,])
    image_link = StringField('Image link')
    genres = SelectMultipleField(
            'Genres', 
            validators=[DataRequired(), valid_genres],
            choices=Genres.choices()
    )
    facebook_link = StringField(
            'Facebook link', 
            validators=[URL(), optional()]
    )
    website = StringField(
           'Website', 
           validators=[URL(), optional()]
    )
    seeking_venue = BooleanField( 'Seeking venue' )
    seeking_description = StringField('Seeking description')


class SearchForm(Form):
    name = StringField('Name') 
    city = StringField('City')
    state = SelectField('State', choices=States.choices_first_blank())    