# -*- coding: UTF-8 -*-
import os
import calendar
import datetime
import requests
import urllib
import json
import math
import sys

from flask import Flask, render_template, request, flash, g, redirect, url_for, session
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import db
from db import get_db
import requests
import urllib
from requests.auth import HTTPBasicAuth
import time
import json

from pprint import pprint

from flask import Flask, render_template, request, flash, g, redirect, url_for, session
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import db
from db import get_db
# from werkzeug.exceptions import abort

# Credentials to be included in heroku
# with open("credentials.txt", "r") as file:
#     API_KEY = file.readline().split()[2]

port = int(os.environ.get("PORT", 5000))

API_KEY = os.environ.get("API_KEY", None)

def create_app(test_config=None):
    #create and configure the app
    app = Flask(__name__, instance_path=os.path.dirname(os.path.abspath(__file__)) + '/instance', instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'final_project.sqlite'),
    )

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/", methods=["GET", "POST"])
    def new():
        if request.method == 'POST':
            mood = request.form["mood"]
            body = request.form["body"].title()
            error = None


            if not mood:
                error = 'Emoji is required.'

            if error is not None:
                flash(error)

            else:
                db = get_db()
                db.execute(
                    'INSERT INTO post (mood, body)'
                    ' VALUES (?, ?)',
                    (mood, body)
                )
                db.commit()
                # flash( "{} because {}" .format(mood , body))
            return redirect(url_for('index'))
        return render_template("new.html")

    @app.route("/index", methods=["GET", "POST"])
    def index():

        db = get_db()
        posts = db.execute(
            'SELECT mood, body'
            ' FROM post'
            ' ORDER BY id DESC '
        ).fetchone()

        return render_template(
            "answer.html",
            posts=posts,
            mood_emoji=mood_emoji,
            )

    @app.route("/mcalendar/", defaults={'month':None, 'year':None},  methods=["GET", "POST"])
    @app.route("/mcalendar/<month>/<year>", methods=["GET", "POST"])
    def mcalendar(month, year):
        if month is None:
            month = datetime.date.today().month
        else:
            month=int(month)
        if year is None:
            year = datetime.date.today().year
        else:
            year=int(year)

        db = get_db()
        posts = db.execute(
            'SELECT id, mood, body, created'
            ' FROM post'
            ' ORDER BY created DESC'
        ).fetchall()

        cal = calendar.Calendar(6)
        today = datetime.date.today().day
        calmonth = cal.monthdatescalendar(year,month)
        previous_month, previous_year= previous_date(month, year)
        next_month, next_year= next_date(month, year)

        posts2 = db.execute(
            'SELECT mood, count(*)'
            ' FROM post'
            ' GROUP BY mood'
        ).fetchall()
        mood_labels = []
        count_mood = []
        for post in posts2:
           mood_labels.append(post['mood'])
           count_mood.append(post['count(*)'])
        total = sum(count_mood)

        return render_template(
            "mcalendar.html",
            posts=posts,
            mood_colour=mood_colour,
            calmonth = calmonth,
            month = month,
            today = today,
            year = year,
            find_mood_for_date = find_mood_for_date,
            mood_emoji = mood_emoji,
            mood_colour_cal=mood_colour_cal,
            previous_month=previous_month,
            previous_year=previous_year,
            next_month=next_month,
            next_year=next_year,
            month_converter=month_converter,
            mood_labels=mood_labels,
            count_mood=count_mood,
            average=average,
            total=total,
            )

    # happy_colour='#eada2c'
    happy_colour='rgb(239, 207, 0, 0.7)'
    # love_colour='#f52394'
    love_colour='rgb(239, 81, 94, 0.4)'
    # enthusiastic_colour='#efa123'
    enthusiastic_colour='rgb(255, 148, 0, 0.7)'
    # nerd_colour="#1093b7"
    nerd_colour='rgb(4, 128, 163, 0.4)'
    # tired_colour="#39894f"
    tired_colour='rgb(57, 137, 79, 0.3)'
    #  worried_colour='#965ec4'
    worried_colour='rgb(86, 20, 104, 0.3)'
    # furious_colour="#ba2112"
    furious_colour='rgb(186, 0, 0, 0.6)'
    # sad_colour='#567477'
    sad_colour='rgb(62, 70, 71, 0.4)'


    def mood_colour(mood):
        if 'Happy' == mood:
            return happy_colour
        elif 'Love' == mood:
            return love_colour
        elif 'Enthusiastic' == mood:
            return enthusiastic_colour
        elif 'Nerd' == mood:
            return nerd_colour
        elif 'Tired' == mood:
            return tired_colour
        elif 'Worried' == mood:
            return worried_colour
        elif 'Furious' == mood:
            return furious_colour
        elif 'Sad' == mood:
            return sad_colour
        else:
            return''

    def find_mood_for_date(date, posts):
        for post in posts:
            if date.strftime("%Y-%m-%d") == post['created'].strftime("%Y-%m-%d"):
                return post['mood']
        return ''

    def mood_emoji(mood):
        if 'Happy' == mood:
            return u'😃'
        elif 'Love' == mood:
            return u'😍'
        elif 'Enthusiastic' == mood:
            return u'🤩'
        elif 'Nerd' == mood:
            return u'🤓'
        elif 'Tired' == mood:
            return u'😴'
        elif 'Worried' == mood:
            return u'😟'
        elif 'Furious' == mood:
            return u'😡'
        elif 'Sad' == mood:
            return u'😥'
        else:
            return ''

    def mood_colour_cal(date, posts):
        for post in posts:
            if date.strftime("%Y-%m-%d") == post['created'].strftime("%Y-%m-%d"):
                mood = post['mood']
                if 'Happy' == mood:
                    return happy_colour
                elif 'Love' == mood:
                    return love_colour
                elif 'Enthusiastic' == mood:
                    return enthusiastic_colour
                elif 'Nerd' == mood:
                    return nerd_colour
                elif 'Tired' == mood:
                    return tired_colour
                elif 'Worried' == mood:
                    return worried_colour
                elif 'Furious' == mood:
                    return furious_colour
                elif 'Sad' == mood:
                    return sad_colour
        return ''

    def previous_date(month , year1):
        pre_month = 0
        new_year = 0
        if month > 1:
            pre_month = month - 1
            new_year = year1
        else:
            pre_month= 12
            new_year = year1 - 1
        return pre_month , new_year

    def next_date(month , year):
        if month < 12:
            month += 1
        else:
            month = 1
            year += 1
        return month , year

    def month_converter(month):
        return calendar.month_abbr[month]


    def average(number, total):
        total_ave= float(number) *100 / total
        return int(round(total_ave))


    @app.route("/gallery", methods=["GET"])
    def gallery():

        db = get_db()
        posts = db.execute(
            'SELECT body, mood'
            ' FROM post'
            ' ORDER BY id DESC '
        ).fetchone()

        mood = posts['mood']
        if 'Happy' == mood:
            flickr_code = 'color_codes=a'
        elif 'Sad' == mood:
            flickr_code = 'color_codes=d'
        elif 'Love' == mood:
            flickr_code = 'color_codes=0'
        elif 'Enthusiastic' == mood:
            flickr_code = 'color_codes=3' ####
        elif 'Nerd' == mood:
            flickr_code = 'color_codes=7' ####
        elif 'Tired' == mood:
            flickr_code = 'color_codes=6' ####
        elif 'Worried' == mood:
            flickr_code = 'color_codes=9' ####
        elif 'Furious' == mood:
            flickr_code = 'color_codes=1' ####

        # with open("credentials.txt", "r") as file:
        #     API_KEY = file.readline().split()[2]


        #Super handy to see if I am getting data -- remember to remove .json() from req to perform this test

        url = 'https://api.flickr.com/services/rest/?method=flickr.photos.search&api_key={}&text={}+{}&sort=relevance&{}&safe_search=1&per_page=20&format=json&nojsoncallback=1'
        req = requests.get(url.format(API_KEY, mood, posts['body'], flickr_code)).json()
        # json_object = r.text
        # return json_object

        gallery_list = list()

        for item in req['photos']['photo']:
            id = item["id"]
            farm = item["farm"]
            server = item["server"]
            secret = item["secret"]
            img_url = "https://farm{}.staticflickr.com/{}/{}_{}.jpg"
            img_url_formated = img_url.format(farm, server, id, secret)
            gallery_list.append(img_url_formated)

        #print (gallery_list)
        body_lower = (posts['body']).upper()

        return render_template(
            "gallery.html",
            posts=posts,
            mood_emoji=mood_emoji,
            gallery_list=gallery_list,
            body_lower=body_lower
            )

    # Spotify App data
    CLIENT_ID = 'f61666ad56b74fbbb4d0b6862df29f95'
    CLIENT_SECRET = 'ba5283bbb94a401ba624d82b78b287f3'


    # Requeest a token without asking user to log in
    def call_api_token():
        endpoint = "https://accounts.spotify.com/api/token"
        make_request = requests.post(endpoint,
                                     data={"grant_type": "client_credentials",
                                           "client_id": CLIENT_ID,
                                           "client_secret": CLIENT_SECRET})
        return make_request


    # Get a token without asking user to log in
    def final():
        spo_response = call_api_token()
        # Check response from Spotify API
        # Something went wrong. Ask user to try again
        if spo_response.status_code != 200:
            return redirect(url_for('music'))
        return spo_response.json()


    # Class that stores token not related to user
    class TokenStorage:
        def __init__(self):
            self.token = None
            self.expire_in = None
            self.start = None

        # Check if token has exired
        def expire(self, time_now):
            if (time_now - self.start) > self.expire_in:
                return True
            return False

        # Get token first time or if expired
        def get_token(self, time_now):
            if self.token is None or self.expire(time_now):
                access_data = final()
                self.token = access_data['access_token']
                self.expire_in = access_data['expires_in']
                self.start = time.time()
            # print self.token
            return self.token


    # Token to access to Spotify data that do not need access to user related data
    # It is stored as class TokenStorage object
    # To get token - TOKEN.get_token(time_now)
    TOKEN = TokenStorage()

    # Create params_query_string
    def params_query_string(payload):
        # Python2 version
        url_arg = urllib.urlencode(payload)

    # Function that replace special characters in val string using the %xx escape
    def quote_params_val(val):
        # Python2 version
        value = urllib.quote(val)
        return value


    def searh_request(token, payload):
        '''
        Search request to Spotify API.
        Can be used both types of tokens.
        Payload specifies what you would like to search (in particular: album,
        playlist, playlist, or track)
        '''
        # Endpoint to search
        # endpoint = 'https://api.spotify.com/v1/search'
        endpoint = 'https://api.spotify.com/v1/recommendations'

        # Use the access token to access Spotify API
        authorization_header = {"Authorization": "Bearer {}".format(token)}
        # Prepare URL for search request
        url_arg = "&".join(["{}={}".format(key, quote_params_val(val))
                           for key, val in payload.items()])
        # url_arg = params_query_string(payload)
        # auth_url = endpoint + "/?" + url_arg
        auth_url = endpoint+"?"+ url_arg
        # Get request to Spotify API to search
        search_response = requests.get(auth_url, headers=authorization_header)
        # Return the response in json format
        return search_response.json()


    def search_tracks(token, query):
        '''
        Function that searches the playlist
        Input: token and playlist name
        Returns: array of arist objects in json format
        '''
        # Specify that we want to search the playlist
        #change query for mood
        if query == "happy":

            payload = {
                    "seed_genres": 'happy',
                    "min_danceability":'0.8',
                    "min_energy":'0.8',
                    }
        elif query == "sad":
            payload = {
                    "seed_genres": 'rainy-day',
                    "min_danceability":'0.1',
                    "min_energy":'0.1',
                    }
        elif query == "love":
            payload = {
                    "seed_genres": 'dance',
                    "min_danceability":'0.5',
                    "min_energy":'0.8',
                    }
        elif query == "enthusiactic":
            payload = {
                    "seed_genres": 'pop',
                    "min_danceability":'0.8',
                    "min_energy":'0.8',
                    }
        elif query == "furious":
            payload = {
                    "seed_genres": 'goth',
                    "min_danceability":'0.4',
                    "min_energy":'0.4',
                    }
        elif query == "nerd" :
            payload = {
                    "seed_genres": 'disco',
                    "min_danceability":'0.5',
                    "min_energy":'0.4',
                    }
        elif query == "tired":
            payload = {
                    "seed_genres": 'ambient',
                    "min_danceability":'0.1',
                    "min_energy":'0.1',
                    }
        elif query == "worried":
            payload = {
                    "seed_genres": 'grunge',
                    "min_danceability":'0.4',
                    "min_energy":'0.5',
                    }
                    
        # Return array of arist objects in json format
        return searh_request(token, payload)


    @app.route("/music")
    def music():
        '''
        Ask user:
        1) playlist to search, see playlist's top tracks, listen 30 sec preview,
        add playlist's top tracks to user's Spotify account new playlist
        2) Search city for upcoming gigs.
        '''
        if "tracks_uri" in session:
            session.pop('tracks_uri', None)
        if "playlist_name" in session:
            session.pop("playlist_name", None)
        return render_template("music.html")


    @app.route("/login")
    def requestAuth():
        """
        Application requests authorization from Spotify.
        Step 1 in Guide
        """
        endpoint = "https://accounts.spotify.com/authorize"
        payload = {
                  "client_id": CLIENT_ID,
                  "response_type": "code",
                  "redirect_uri": REDIRECT_URI,
                  # "state": "sdfdskjfhkdshfkj",
                  "scope": "playlist-modify-public user-read-private",
                  # "show_dialog": True
                }

        # Create query string from params
        # url_arg = "&".join(["{}={}".format(key, quote_params_val(val)) for
        #                    key, val in params.items()])
        url_arg = params_query_string(payload)

        # Request URL
        auth_url = endpoint + "/?" + url_arg
        #print "AUTH_URL", auth_url
        # User is redirected to Spotify where user is asked to authorize access to
        # his/her account within the scopes
        return redirect(auth_url)



    @app.route("/search_tracks", methods=["POST"])
    def tracks_search():
        """
        This decorator searches the track by name
        Returns:
        1) Template with found playlists that match user input
        2) Template that asks to repeat playlist search in case of
        previous unsuccessful attempt.
        """
        # Check if user is logged in
        #if "access_data" not in session:
        #     return redirect(url_for('index'))
        # User is logged in
        # # Get access token from user's request
        # token = session['access_data']['access_token']

        # Not related to user token is stored as class TokenStorage object
        token = TOKEN.get_token(time.time())

        # Get data that user post to app on index page
        form_data = request.form
        track = form_data["track"]

        # Get data in json format from search_playlist request
        found_tracks = search_tracks(token, track)

        return render_template("req_to_show_tracks.html",found_tracks=found_tracks,)


        db.init_app(app)

    return app

if __name__ == "__main__":
    create_app().run(host='0.0.0.0', debug=True, port=port)
