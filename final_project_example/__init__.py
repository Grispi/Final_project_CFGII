import os
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
        return render_template("history.html",  posts=posts, mood_colour=mood_colour)

    def mood_colour(mood):
        if 'happy' == mood:
            mood_c = '#aa80ff'
        elif 'sad' == mood:
            mood_c = '#b3b000'
        elif 'love' == mood:
            mood_c = '#668cff'
        else:
            mood_c = ''
        return mood_c

   
    from . import db
    db.init_app(app)

    return app







