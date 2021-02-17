# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
from datetime import date
from flask import jsonify
from models import db, Venue, Artist, Shows

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object("config")
db.init_app(app)
migrate = Migrate(app, db)


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format="medium"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters["datetime"] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route("/")
def index():
    venues = Venue.query.order_by(Venue.created_date.desc()).limit(10).all()
    artists = Artist.query.order_by(Artist.created_date.desc()).limit(10).all()
    return render_template("pages/home.html", venues=venues, artists=artists)


#  Venues
#  ----------------------------------------------------------------


@app.route("/venues")
def venues():

    data_list = []
    distinct_states = Venue.query.with_entities(Venue.state).distinct()

    for state in distinct_states:
        data_dictionary = {}
        data_dictionary["state"] = state[0]
        distinct_cities = Venue.query.with_entities(Venue.city).distinct()
        for city in distinct_cities:
            data_dictionary["city"] = city[0]
            venues_by_states = Venue.query.filter_by(state=state, city=city).all()
            venue_list = []
            for venue_by_state in venues_by_states:

                venue_dictionary = {}
                venue_dictionary["id"] = venue_by_state.id
                venue_dictionary["name"] = venue_by_state.name
                upcoming_shows = Shows.query.filter(
                    Shows.venue_id == venue_by_state.id,
                    Shows.start_time >= datetime.now(),
                ).count()
                venue_dictionary["num_upcoming_shows"] = upcoming_shows
                venue_list.append(venue_dictionary)

            data_dictionary["venues"] = venue_list
            data_list.append(data_dictionary)

    return render_template("pages/venues.html", areas=data_list)


@app.route("/venues/search", methods=["POST"])
def search_venues():

    venue_term = request.form["search_term"]
    venues = Venue.query.filter(Venue.name.ilike("%" + venue_term + "%"))
    result = {}
    result["count"] = venues.count()
    result_list = []
    for venue in venues:
        result_dictionary = {}
        result_dictionary["id"] = venue.id
        result_dictionary["name"] = venue.name
        result_dictionary["num_upcoming_shows"] = Shows.query.filter_by(
            venue_id=venue.id
        ).count()
        result_list.append(result_dictionary)
    result["data"] = result_list

    return render_template(
        "pages/search_venues.html",
        results=result,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):

    data_list = []

    venues = Venue.query.all()
    for venue in venues:
        venue_data = {}
        venue_data["id"] = venue.id
        venue_data["name"] = venue.name
        venue_data["genres"] = [
            item.replace('"', "") for item in venue.genres[1:-1].split(",")
        ]
        venue_data["address"] = venue.address
        venue_data["city"] = venue.city
        venue_data["state"] = venue.state
        venue_data["phone"] = venue.phone
        venue_data["website"] = venue.website
        venue_data["facebook_link"] = venue.facebook_link
        venue_data["seeking_talent"] = venue.seeking_talent
        venue_data["image_link"] = venue.image_link
        upcoming_show_list = []
        data_query_shows = (
            db.session.query(Shows, Artist)
            .join(Artist, Shows.artists)
            .filter(Shows.start_time >= datetime.now())
        ).all()
        for row in data_query_shows:
            upcomping_show_data = {}
            upcomping_show_data["artist_id"] = row.Artist.id
            upcomping_show_data["artist_name"] = row.Artist.name
            upcomping_show_data["artist_image_link"] = row.Artist.image_link
            upcomping_show_data["start_time"] = str(row.Shows.start_time)
            upcoming_show_list.append(upcomping_show_data)

        venue_data["upcoming_shows"] = upcoming_show_list
        venue_data["upcoming_shows_count"] = len(data_query_shows)
        past_show_list = []
        data_query_past_shows = (
            db.session.query(Shows, Artist)
            .join(Artist, Shows.artists)
            .filter(Shows.start_time < datetime.now())
        ).all()
        for row in data_query_past_shows:
            past_show_data = {}
            past_show_data["artist_id"] = row.Artist.id
            past_show_data["artist_name"] = row.Artist.name
            past_show_data["artist_image_link"] = row.Artist.image_link
            past_show_data["start_time"] = str(row.Shows.start_time)
            past_show_list.append(past_show_data)

        venue_data["past_shows_count"] = len(data_query_past_shows)
        venue_data["past_shows"] = past_show_list
        data_list.append(venue_data)

    data = list(filter(lambda d: d["id"] == venue_id, data_list))[0]
    return render_template("pages/show_venue.html", venue=data)


#  Create Venue
#  ----------------------------------------------------------------


@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
    form = VenueForm(request.form)
    if not form.validate():
        return render_template("forms/new_venue.html", form=form)

    name = form.name.data
    try:
        venue_duplicate = Venue.query.filter_by(name=name).first()
        if venue_duplicate is not None:
            flash(
                "An error occurred. Venue "
                + venue_duplicate.name
                + " already exists, it could not be listed."
            )
            return render_template("forms/new_venue.html", form=form)

        city = form.city.data
        state = form.state.data
        address = form.address.data
        phone = form.phone.data
        image_link = form.image_link.data
        genres = form.genres.data
        created_date = datetime.now()
        seeking_talent = form.seeking_talent.data
        seeking_description = form.seeking_description.data
        website = form.website.data
        facebook_link = form.facebook_link.data
        venue = Venue(
            name=name,
            city=city,
            state=state,
            address=address,
            phone=phone,
            image_link=image_link,
            genres=genres,
            created_date=created_date,
            seeking_talent=seeking_talent,
            seeking_description=seeking_description,
            website=website,
            facebook_link=facebook_link,
        )

        form.populate_obj(venue)
        db.session.add(venue)
        db.session.commit()
        flash("Venue " + name + " was successfully listed!")
    except Exception as e:
        db.session.rollback()
        print(e)
        flash("An error occurred. Venue " + name + " could not be listed.")
    finally:
        db.session.close()
    return render_template("pages/home.html")


@app.route("/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None


#  Artists
#  ----------------------------------------------------------------
@app.route("/artists")
def artists():
    artist_data = Artist.query.all()
    return render_template("pages/artists.html", artists=artist_data)


@app.route("/artists/search", methods=["POST"])
def search_artists():

    artist_term = request.form["search_term"]
    artists = Artist.query.filter(Artist.name.ilike("%" + artist_term + "%"))
    result = {}
    result["count"] = artists.count()
    result_list = []
    for venue in artists:
        result_dictionary = {}
        result_dictionary["id"] = venue.id
        result_dictionary["name"] = venue.name
        result_dictionary["num_upcoming_shows"] = Shows.query.filter_by(
            venue_id=venue.id
        ).count()
        result_list.append(result_dictionary)
    result["data"] = result_list

    return render_template(
        "pages/search_artists.html",
        results=result,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):

    data_list = []

    artists = Artist.query.all()
    for artist in artists:
        artist_data = {}
        artist_data["id"] = artist.id
        artist_data["name"] = artist.name
        artist_data["genres"] = [
            item.replace('"', "") for item in artist.genres[1:-1].split(",")
        ]
        artist_data["city"] = artist.city
        artist_data["state"] = artist.state
        artist_data["phone"] = artist.phone
        artist_data["website"] = artist.website
        artist_data["facebook_link"] = artist.facebook_link
        artist_data["seeking_venue"] = artist.seeking_venue
        artist_data["seeking_description"] = artist.seeking_description
        artist_data["image_link"] = artist.image_link
        upcoming_show_list = []
        data_query_shows = (
            db.session.query(Shows, Venue)
            .join(Venue, Shows.venues)
            .filter(Shows.start_time >= datetime.now())
        ).all()
        for row in data_query_shows:
            upcomping_show_data = {}
            upcomping_show_data["artist_id"] = row.Venue.id
            upcomping_show_data["artist_name"] = row.Venue.name
            upcomping_show_data["artist_image_link"] = row.Venue.image_link
            upcomping_show_data["start_time"] = str(row.Shows.start_time)
            upcoming_show_list.append(upcomping_show_data)

        artist_data["upcoming_shows"] = upcoming_show_list
        artist_data["upcoming_shows_count"] = len(data_query_shows)
        past_show_list = []
        data_query_past_shows = (
            db.session.query(Shows, Venue)
            .join(Venue, Shows.venues)
            .filter(Shows.start_time < datetime.now())
        ).all()
        for row in data_query_past_shows:
            past_show_data = {}
            past_show_data["artist_id"] = row.Venue.id
            past_show_data["artist_name"] = row.Venue.name
            past_show_data["artist_image_link"] = row.Venue.image_link
            past_show_data["start_time"] = str(row.Shows.start_time)
            past_show_list.append(past_show_data)

        artist_data["past_shows_count"] = len(data_query_past_shows)
        artist_data["past_shows"] = past_show_list
        data_list.append(artist_data)

    data = list(filter(lambda d: d["id"] == artist_id, data_list))[0]
    return render_template("pages/show_artist.html", artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = {
        "id": 4,
        "name": "Guns N Petals",
        "genres": ["Rock n Roll"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "326-123-5000",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    }
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template("forms/edit_artist.html", form=form, artist=artist)


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    return redirect(url_for("show_artist", artist_id=artist_id))


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    form = VenueForm()
    venue = {
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
        "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    }
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template("forms/edit_venue.html", form=form, venue=venue)


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    return redirect(url_for("show_venue", venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------


@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
    form = ArtistForm(request.form)
    if not form.validate():
        return render_template("forms/new_artist.html", form=form)

    name = form.name.data
    try:
        artist_duplicate = Artist.query.filter_by(name=name).first()
        if artist_duplicate is not None:
            flash(
                "An error occurred. Artist "
                + artist_duplicate.name
                + " already exists, it could not be listed."
            )
            return render_template("forms/new_artist.html", form=form)
        city = form.city.data
        state = form.state.data
        phone = form.phone.data
        image_link = form.image_link.data
        genres = form.genres.data
        website = form.website.data
        created_date = datetime.now()
        seeking_venue = form.seeking_venue.data
        seeking_description = form.seeking_description.data
        facebook_link = form.facebook_link.data
        artist = Artist(
            name=name,
            city=city,
            state=state,
            phone=phone,
            image_link=image_link,
            genres=genres,
            website=website,
            created_date=created_date,
            seeking_venue=seeking_venue,
            seeking_description=seeking_description,
            facebook_link=facebook_link,
        )

        db.session.add(artist)
        db.session.commit()
        flash("Artist " + request.form["name"] + " was successfully listed!")
    except Exception as e:
        db.session.rollback()
        print(e)
        flash("An error occurred. Artist " + name + " could not be listed.")
    finally:
        db.session.close()

    return render_template("pages/home.html")


#  Shows
#  ----------------------------------------------------------------


@app.route("/shows")
def shows():

    shows_data = []
    data_query = (
        db.session.query(Shows, Artist, Venue)
        .join(Artist, Shows.artists)
        .join(Venue, Shows.venues)
    ).all()

    for row in data_query:
        row_dictionary = {}
        row_dictionary["venue_id"] = row.Venue.id
        row_dictionary["venue_name"] = row.Venue.name
        row_dictionary["artist_id"] = row.Artist.id
        row_dictionary["artist_name"] = row.Artist.name
        row_dictionary["artist_image_link"] = row.Artist.image_link
        row_dictionary["start_time"] = str(row.Shows.start_time)
        shows_data.append(row_dictionary)

    return render_template("pages/shows.html", shows=shows_data)


@app.route("/shows/create")
def create_shows():
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():
    form = ShowForm(request.form)
    if not form.validate():
        return render_template("forms/new_show.html", form=form)
    try:
        artist_id = form.artist_id.data
        venue_id = form.venue_id.data
        start_time = form.start_time.data

        show_is_exists = Shows.query.filter_by(
            artist_id=artist_id, venue_id=venue_id
        ).all()
        if show_is_exists:
            flash("This show already exists")
            return render_template("forms/new_show.html", form=form)

        show = Shows(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
        db.session.add(show)
        db.session.commit()
        flash("Show was successfully listed!")
    except Exception as e:
        print(e)
        db.session.rollback()
        flash("An error occurred.")
    finally:
        db.session.close()
    return render_template("pages/home.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


@app.errorhandler(400)
def bad_request_error(error):
    return render_template("errors/400.html"), 400


@app.errorhandler(405)
def invalid_method_error(error):
    return render_template("errors/405.html"), 405


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == "__main__":
    app.run()

# Or specify port manually:
"""
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
"""
