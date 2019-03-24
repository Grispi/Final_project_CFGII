# -*- coding: UTF-8 -*-
import os
import calendar
import datetime
import emoji
import requests

from flask import Flask, render_template, request, flash, g, redirect, url_for
from final_project_example.db import get_db
from werkzeug.exceptions import abort

API_KEY = "a33ea2b039e32abade45a6e1b1b87670"

def create_app(test_config=None):
    #create and configure the app
    app = Flask(__name__, instance_relative_config=True)
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



    @app.route("/history", methods=["GET", "POST"])
    def history():

        db = get_db()
        posts = db.execute(
            'SELECT id, mood, body, created'
            ' FROM post'
            ' ORDER BY created DESC'
        ).fetchall()

        # date_mood_time= date_mood.strftime("%d-%m-%Y")
        cal = calendar.Calendar(6)
        today = datetime.date.today().day
        month = datetime.date.today().month
        year = datetime.date.today().year
        calmonth = cal.monthdatescalendar(year,month)
        return render_template(
            "history.html",
            posts=posts,
            mood_colour=mood_colour,
            calmonth = calmonth,
            month = month,
            today = today,
            find_mood_for_date = find_mood_for_date,
            mood_emoji = mood_emoji,
            mood_colour_cal=mood_colour_cal,
            )

    happy_colour='#f52394'
    sad_colour='#7c7c7c'
    love_colour='#ff2000'

    def mood_colour(mood):
        if 'Happy' == mood:
            return happy_colour
        elif 'Sad' == mood:
            return sad_colour
        elif 'Love' == mood:
            return love_colour
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
        elif 'Sad' == mood:
            return u'😥'
        elif 'Love' == mood:
            return u'😍'
        else:
            return ''


    def mood_colour_cal(date, posts):
        for post in posts:
            if date.strftime("%Y-%m-%d") == post['created'].strftime("%Y-%m-%d"):
                mood = post['mood']
                if 'Happy' == mood:
                    return happy_colour
                    # return '#ef871a'
                    # return '#ffa342'
                elif 'Sad' == mood:
                    return sad_colour
                    # return '#4d4d4f'
                    # return '#2b356b'
                elif 'Love' == mood:
                    # return '#e81717'
                    # return  '#ffb6b2'
                    return love_colour
        return ''

    @app.route("/graph", methods=["GET", "POST"])
    def graph():
        db = get_db()
        posts = db.execute(
            'SELECT mood, count(*)'
            ' FROM post'
            ' GROUP BY mood'
        ).fetchall()
        mood_labels = []
        count_mood = []
        for post in posts:
           mood_labels.append(post['mood'])
           count_mood.append(post['count(*)'])

        return render_template(
            "graph.html",
            posts=posts,
            mood_colour=mood_colour,
            mood_emoji = mood_emoji,
            mood_colour_cal=mood_colour_cal,
            mood_labels = mood_labels,
            count_mood = count_mood,
            )
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

    @app.route("/gallery", methods=["GET", "POST"])
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

        #Super handy to see if I am getting data -- remember to remove .json() from r to perform this test

        url = 'https://api.flickr.com/services/rest/?method=flickr.photos.search&api_key=' + API_KEY + '&text={}+{}&sort=relevance&{}&safe_search=1&per_page=20&format=json&nojsoncallback=1'
        r = requests.get(url.format(mood,posts['body'], flickr_code)).json()
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
        body_lower = (posts['body']).upper()

        return render_template(
            "gallery.html",
            posts=posts,
            mood_emoji=mood_emoji,
            gallery_list=gallery_list,
            body_lower=body_lower
            )

    @app.route("/music", methods=["GET", "POST"])
    def music():

        db = get_db()
        posts = db.execute(
            'SELECT mood'
            ' FROM post'
            ' ORDER BY id DESC '
        ).fetchone()

        return render_template(
            "music.html",
            posts=posts,
            mood_emoji=mood_emoji,
            )

    from . import db
    db.init_app(app)

    return app
