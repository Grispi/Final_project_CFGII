# -*- coding: UTF-8 -*-
import os
import calendar
import datetime
import requests
import math
import sys

from flask import Flask, render_template, request, flash, g, redirect, url_for
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import db
from db import get_db
# from werkzeug.exceptions import abort

# Credentials to be included in heroki
with open("credentials.txt", "r") as file:
    API_KEY = file.readline().split()[2]


port = int(os.environ.get("PORT", 5000))


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

    # @app.route("/mcalendar", methods=["GET", "POST"])
    # def graph():
    #     db = get_db()
    #     posts2 = db.execute(
    #         'SELECT mood, count(*)'
    #         ' FROM post'
    #         ' GROUP BY mood'
    #     ).fetchall()
    #     mood_labels = []
    #     count_mood = []
    #     for post in posts2:
    #        mood_labels.append(post['mood'])
    #        count_mood.append(post['count(*)'])
    #     total = sum(count_mood)

    #     return render_template(
    #         "mcalendar.html",
    #         posts2=posts2,
    #         mood_colour=mood_colour,
    #         mood_emoji = mood_emoji,
    #         mood_labels = mood_labels,
    #         count_mood = count_mood,
    #         total=total,
    #         average=average,
    #         )


    # @app.route("/graph", methods=["GET", "POST"])
    # def graph():
    #     db = get_db()
    #     posts = db.execute(
    #         'SELECT mood, count(*)'
    #         ' FROM post'
    #         ' GROUP BY mood'
    #     ).fetchall()
    #     mood_labels = []
    #     count_mood = []
    #     for post in posts:
    #        mood_labels.append(post['mood'])
    #        count_mood.append(post['count(*)'])
    #     total = sum(count_mood)

    #     return render_template(
    #         "graph.html",
    #         posts=posts,
    #         mood_colour=mood_colour,
    #         mood_emoji = mood_emoji,
    #         mood_labels = mood_labels,
    #         count_mood = count_mood,
    #         total=total,
    #         average=average,
    #         )

    def average(number, total):
        total_ave= float(number) *100 / total
        return int(round(total_ave))


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

        with open("credentials.txt", "r") as file:
            API_KEY = file.readline().split()[2]


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


    db.init_app(app)

    return app

if __name__ == "__main__":
    create_app().run(host='0.0.0.0', debug=True, port=port)
