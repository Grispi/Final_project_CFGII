# -*- coding: UTF-8 -*-
import os
import calendar
import datetime
import emoji
from flask import Flask, render_template, request, flash, g, redirect, url_for
from final_project_example.db import get_db
from werkzeug.exceptions import abort


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
            body = request.form["body"]
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


    @app.route("/history/", defaults={'month':None, 'year':None},  methods=["GET", "POST"])
    @app.route("/history/<month>/<year>", methods=["GET", "POST"])
    def history(month, year):
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

        return render_template(
            "history.html",
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
            )

    happy_colour='#ffce0c'
    sad_colour='#567477'
    love_colour='#f4857f'

    def mood_colour(mood):
        if 'happy' == mood:
            return happy_colour
        elif 'sad' == mood:
            return sad_colour
        elif 'love' == mood:
            return love_colour
        else:
            return''

    def find_mood_for_date(date, posts):
        for post in posts:
            if date.strftime("%Y-%m-%d") == post['created'].strftime("%Y-%m-%d"):
                return post['mood']
        return ''

    def mood_emoji(mood):
        if 'happy' == mood:
            return u'😃'
        elif 'sad' == mood:
            return u'😥'
        elif 'love' == mood:
            return u'😍'
        else:
            return ''

    def mood_colour_cal(date, posts):
        for post in posts:
            if date.strftime("%Y-%m-%d") == post['created'].strftime("%Y-%m-%d"):
                mood = post['mood']
                if 'happy' == mood:
                    return happy_colour
                    # return '#ef871a'
                    # return '#ffa342'
                elif 'sad' == mood:
                    return sad_colour
                    # return '#4d4d4f'
                    # return '#2b356b'
                elif 'love' == mood:
                    # return '#e81717'
                    # return  '#ffb6b2'
                    return love_colour
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
  
    @app.route("/gallery", methods=["GET", "POST"])
    def gallery():

        db = get_db()
        posts = db.execute(
            'SELECT mood'
            ' FROM post'
            ' ORDER BY id DESC '
        ).fetchone()

        return render_template(
            "gallery.html",
            posts=posts,
            mood_emoji=mood_emoji,
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
