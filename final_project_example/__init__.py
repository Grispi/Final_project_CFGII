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
                flash( "The user is {} because {}" .format(mood , body))
            return redirect(url_for('index'))
        return render_template("new.html")

    

    @app.route("/index", methods=["GET", "POST"])
    def index():

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
            )

    def mood_colour(mood):
        if 'happy' == mood:
            return '#aa80ff'
        elif 'sad' == mood:
            return '#b3b000'
        elif 'love' == mood:
            return '#668cff'
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



    from . import db
    db.init_app(app)

    return app







