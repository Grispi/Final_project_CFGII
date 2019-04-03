# -*- coding: UTF-8 -*-
import os
import calendar
import datetime
import requests
import urllib
import json
import math
import sys
import time
import urllib

from flask import Flask, render_template, request, flash, g, redirect, url_for, session
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from requests.auth import HTTPBasicAuth

import db
from db import get_db

# Port configuration for Heroku
port = int(os.environ.get("PORT", 5000))

# Flickr Key
API_KEY = os.environ.get("API_KEY", None)

# Spotify App data
CLIENT_ID = os.environ.get("CLIENT_ID", None)
CLIENT_SECRET = os.environ.get("CLIENT_SECRET", None)

def create_app(test_config=None):
    #create and configure the app and database
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
        # get the information from the form
        if request.method == 'POST':
            mood = request.form["mood"]
            body = request.form["body"].title()
            error = None

            if not mood:
                error = 'Emoji is required.'

            if error is not None:
                flash(error)
    
            # include data from the user in the database
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
    # Show the last mood and keyword from the database
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

    # HISTORY
    @app.route("/mcalendar/", defaults={'month':None, 'year':None},  methods=["GET", "POST"])
    @app.route("/mcalendar/<month>/<year>", methods=["GET", "POST"])
    def mcalendar(month, year):
        # Calendar setting month/year for Today - default day
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

        # Start the calendar in Sunday
        cal = calendar.Calendar(6)

        today = datetime.date.today().day
        calmonth = cal.monthdatescalendar(year,month)

        # previous/next month-year functions
        previous_month, previous_year= previous_date(month, year)
        next_month, next_year= next_date(month, year)

        # information from the database for the graphic. 
        # Count(*)->returns the number of rows that matches with the same mood
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

    # Mood Colours: 
    # happy
    # happy_colour='rgb(239, 207, 0, 0.7)'
    # # love
    # love_colour='rgb(239, 81, 94, 0.4)'
    # # enthusiastic
    # enthusiastic_colour='rgb(255, 148, 0, 0.7)'
    # # nerd
    # nerd_colour='rgb(4, 128, 163, 0.4)'
    # # tired
    # tired_colour='rgb(57, 137, 79, 0.3)'
    # # worried
    # worried_colour='rgb(86, 20, 104, 0.3)'
    # # furious
    # furious_colour='rgb(186, 0, 0, 0.6)'
    # # sad
    # sad_colour='rgb(62, 70, 71, 0.4)'


    def mood_colour(mood):
        if 'Happy' == mood:
            return 'happy_colour'
        elif 'Love' == mood:
            return 'love_colour'
        elif 'Enthusiastic' == mood:
            return 'enthusiastic_colour'
        elif 'Nerd' == mood:
            return 'nerd_colour'
        elif 'Tired' == mood:
            return 'tired_colour'
        elif 'Worried' == mood:
            return 'worried_colour'
        elif 'Furious' == mood:
            return 'furious_colour'
        elif 'Sad' == mood:
            return 'sad_colour'
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
                    return 'happy_colour'
                elif 'Love' == mood:
                    return 'love_colour'
                elif 'Enthusiastic' == mood:
                    return 'enthusiastic_colour'
                elif 'Nerd' == mood:
                    return 'nerd_colour'
                elif 'Tired' == mood:
                    return 'tired_colour'
                elif 'Worried' == mood:
                    return 'worried_colour'
                elif 'Furious' == mood:
                    return 'furious_colour'
                elif 'Sad' == mood:
                    return 'sad_colour'
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
        # return the number month to letters in abbreviated form.
        return calendar.month_abbr[month]


    def average(number, total):
        # average operation and round numbers in order to have total = 100%
        total_ave= float(number) *100 / total
        return int(round(total_ave))


    # GALLERY
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

    @app.route("/gallery2", methods=["GET", "POST"])
    def gallery_search():
        text = request.form["Text"]

        # Super handy to see if I am getting data -- remember to remove .json() from req to perform this test

        url = 'https://api.flickr.com/services/rest/?method=flickr.photos.search&api_key={}&text={}&sort=relevance&safe_search=1&per_page=20&format=json&nojsoncallback=1'
        r = requests.get(url.format(API_KEY, text)).json()
        # json_object = r.text
        # return json_object

        gallery_list = list()

        for item in r['photos']['photo']:
            id = item["id"]
            farm = item["farm"]
            server = item["server"]
            secret = item["secret"]
            img_url = "https://farm{}.staticflickr.com/{}/{}_{}.jpg"
            img_url_formated = img_url.format(farm, server, id, secret)
            gallery_list.append(img_url_formated)

        #print (gallery_list)

        return render_template(
            "gallery2.html",
            gallery_list=gallery_list,
            )

    # MUSIC
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
     
        auth_url = endpoint+"?"+ url_arg
        # Get request to Spotify API to search
        search_response = requests.get(auth_url, headers=authorization_header)
        # Return the response in json format
        return search_response.json()


    def search_tracks(token, query):
        '''
        Function that searches tracks which match with the query parameters 
        for spotify recommendations by moods.
        Input: token and playlist name
        Returns: array of tracks objects in json format
        '''
        # Get Mood from the database
        db = get_db()
        posts = db.execute(
            'SELECT body, mood'
            ' FROM post'
            ' ORDER BY id DESC '
        ).fetchone()

        # change query for mood
        mood = posts['mood']

        # Seed/Query parameters for spotify recommendations by moods
        if query == "Happy":
            payload = {
                    "seed_genres": 'happy',
                    "min_danceability":'0.8',
                    "min_energy":'0.8',
                    }
        elif query == "Sad":
            payload = {
                    "seed_genres": 'rainy-day',
                    "min_danceability":'0.1',
                    "min_energy":'0.1',
                    }
        elif query == "Love":
            payload = {
                    "seed_genres": 'dance',
                    "min_danceability":'0.5',
                    "min_energy":'0.8',
                    }
        elif query == "Enthusiastic":
            payload = {
                    "seed_genres": 'pop',
                    "min_danceability":'0.8',
                    "min_energy":'0.8',
                    }
        elif query == "Furious":
            payload = {
                    "seed_genres": 'goth',
                    "min_danceability":'0.4',
                    "min_energy":'0.4',
                    }
        elif query == "Nerd" :
            payload = {
                    "seed_genres": 'disco',
                    "min_danceability":'0.5',
                    "min_energy":'0.4',
                    }
        elif query == "Tired":
            payload = {
                    "seed_genres": 'ambient',
                    "min_danceability":'0.1',
                    "min_energy":'0.1',
                    }
        elif query == "Worried":
            payload = {
                    "seed_genres": 'grunge',
                    "min_danceability":'0.4',
                    "min_energy":'0.5',
                    }

        # Return array of track objects in json format
        return searh_request(token, payload)


    @app.route("/music")
    def music():
        '''
        Ask database:
        1) mood to search, 
        Searching tracks with recommendations for this mood in spotify 
        2) generated based on for a given seed entity and matched against similar artists and tracks,
        listen 30 sec preview,
        '''
        db = get_db()
        posts = db.execute(
            'SELECT body, mood'
            ' FROM post'
            ' ORDER BY id DESC '
        ).fetchone()
        mood = posts['mood']

        # Not related to user token is stored as class TokenStorage object
        token = TOKEN.get_token(time.time())

        # Get data that user post to app on index page
        track = mood

        # Get data in json format from search_tracks request
        found_tracks = search_tracks(token, track)

        return render_template("music.html",
            posts=posts,
            mood=mood,
            mood_emoji = mood_emoji,
            found_tracks=found_tracks,)


        db.init_app(app)

    return app

if __name__ == "__main__":
    create_app().run(host='0.0.0.0', debug=True, port=port)
