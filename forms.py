from datetime import datetime
from flask_wtf import Form
from wtforms import (
    StringField,
    SelectField,
    SelectMultipleField,
    DateTimeField,
    widgets,
    BooleanField,
    IntegerField,
    ValidationError,
)
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, AnyOf, URL
from enum import Enum
import phonenumbers


class ShowForm(Form):

    # artist_id = IntegerField("artist_id")
    # venue_id = IntegerField("venue_id")
    artist_id = SelectField("artist_id", validators=[DataRequired()], choices=[])
    venue_id = SelectField("venue_id", validators=[DataRequired()], choices=[])
    # artist_id.choices = [(a.id, a.name) for a in Artist.query.all()]

    # def __init__(self, artists=None, venues=None):
    #     super().__init__()
    #     if artists:
    #         self.artist_id.choices = [(a.id, a.name) for a in artists]
    #     if venues:
    #         self.venue_id.choices = [(v.id, v.name) for v in venues]

    start_time = DateTimeField(
        "start_time", validators=[DataRequired()], default=datetime.today()
    )


class State(Enum):
    AL = "AL"
    AK = "AK"
    AZ = "AZ"
    AR = "AR"
    CA = "CA"
    CO = "CO"
    CT = "CT"
    DE = "DE"
    DC = "DC"
    FL = "FL"
    GA = "GA"
    HI = "HI"
    ID = "ID"
    IL = "IL"
    IN = "IN"
    IA = "IA"
    KS = "KS"
    KY = "KY"
    LA = "LA"
    ME = "ME"
    MT = "MT"
    NE = "NE"
    NV = "NV"
    NH = "NH"
    NJ = "NJ"
    NM = "NM"
    NY = "NY"
    NC = "NC"
    ND = "ND"
    OH = "OH"
    OK = "OK"
    OR = "OR"
    MD = "MD"
    MA = "MA"
    MI = "MI"
    MN = "MN"
    MS = "MS"
    MO = "MO"
    PA = "PA"
    RI = "RI"
    SC = "SC"
    SD = "SD"
    TN = "TN"
    TX = "TX"
    UT = "UT"
    VT = "VT"
    VA = "VA"
    WA = "WA"
    WV = "WV"
    WI = "WI"
    WY = "WY"


class Genres(Enum):
    Alternative = "Alternative"
    Blues = "Blues"
    Classical = "Classical"
    Country = "Country"
    Electronic = "Electronic"
    Folk = "Folk"
    Funk = "Funk"
    Hip_Hop = "Hip-Hop"
    Heavy_Metal = "Heavy Metal"
    Instrumental = "Instrumental"
    Jazz = "Jazz"
    Musical_Theatre = "Musical Theatre"
    Pop = "Pop"
    Punk = "Punk"
    R_B = "R&B"
    Reggae = "Reggae"
    Rock_n_Roll = "Rock n Roll"
    Soul = "Soul"
    Other = "Other"


def validate_phone(self, field):
    if len(field.data) != 10:
        raise ValidationError("Invalid phone number.")
    try:
        input_number = phonenumbers.parse(field.data)
        if not (phonenumbers.is_valid_number(input_number)):
            raise ValidationError("Invalid phone number format")
    except Exception as e:
        print(e)


class VenueForm(Form):
    name = StringField("name", validators=[DataRequired()])
    city = StringField("city", validators=[DataRequired()])
    state = SelectField(
        "state",
        validators=[DataRequired()],
        choices=[(member.value, name) for name, member in State.__members__.items()],
    )
    address = StringField("address", validators=[DataRequired()])
    phone = StringField("phone", validators=[validate_phone])
    image_link = StringField("image_link")
    genres = SelectMultipleField(
        "genres",
        validators=[DataRequired()],
        choices=[
            (member.value, member.value) for name, member in Genres.__members__.items()
        ],
    )
    image_link = StringField("image_link", validators=[DataRequired(), URL()])
    website = StringField("website", validators=[DataRequired(), URL()])
    facebook_link = StringField("facebook_link", validators=[DataRequired(), URL()])
    seeking_talent = BooleanField("Seeking talent")
    seeking_description = StringField(
        "seeking_description", validators=[DataRequired()], widget=TextArea()
    )


class ArtistForm(Form):
    name = StringField("name", validators=[DataRequired()])
    city = StringField("city", validators=[DataRequired()])
    state = SelectField(
        "state",
        validators=[DataRequired()],
        choices=[(member.value, name) for name, member in State.__members__.items()],
    )
    phone = StringField(
        "phone",
        validators=[DataRequired(), validate_phone],
    )
    image_link = StringField("image_link", validators=[DataRequired(), URL()])
    genres = SelectMultipleField(
        "genres",
        validators=[DataRequired()],
        choices=[
            (member.value, member.value) for name, member in Genres.__members__.items()
        ],
    )
    seeking_venue = BooleanField("Seeking venue")
    seeking_description = StringField(
        "seeking_description", validators=[DataRequired()], widget=TextArea()
    )
    website = StringField("website", validators=[DataRequired(), URL()])

    facebook_link = StringField(
        "facebook_link",
        validators=[DataRequired(), URL()],
    )
