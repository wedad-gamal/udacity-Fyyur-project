# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()


class Shows(db.Model):
    __tablename__ = "Show"
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), primary_key=True)
    start_time = db.Column(db.DateTime)
    venue = db.relationship("Venue", backref=db.backref("show_artists", lazy=True))
    artist = db.relationship("Artist", backref=db.backref("show_venues", lazy=True))

    def _repr__(self):
        return f"<Shows {self.venue_id} {self.artist_id}>"


class Venue(db.Model):
    __tablename__ = "Venue"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(500))
    created_date = db.Column(db.DateTime)
    facebook_link = db.Column(db.String(500), nullable=False)
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(300), nullable=True)
    artists = db.relationship("Shows", backref=db.backref("venues", lazy=True))

    def _repr__(self):
        return f"<Venue {self.id} {self.name}>"


class Artist(db.Model):
    __tablename__ = "Artist"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    created_date = db.Column(db.DateTime)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(500))
    website = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String())
    Venues = db.relationship("Shows", backref=db.backref("artists", lazy=True))

    def _repr__(self):
        return f"<Artist {self.id} {self.name}>"
