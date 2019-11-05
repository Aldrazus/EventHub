from flask import Blueprint, render_template, request, session, url_for, redirect, flash
from werkzeug.urls import url_parse
from app.models import User, Event
from flask_login import current_user, login_user, logout_user, login_required
from forms import PostForm
from app import db
import config


mod = Blueprint('organizer', __name__,
                        template_folder='app/templates')


#some code from Miguel Grinberg's blog
#https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
@mod.route('/')
@login_required
def index():
    return render_template("home.html", title="Home")

@mod.route('/post', methods=['GET', 'POST'])
@login_required
def post():
    form = PostForm()
    if form.validate_on_submit():
        event = Event(event_name=form.event_name.data, 
            owner_id=current_user.id, 
            description=form.event_desc.data, 
            start_time=form.start.data, 
            end_time=form.end.data, 
            location=form.location.data
        )
        db.session.add(event)
        db.session.commit()

        if False: #do some checks on the form
            flash('Invalid data')
            return redirect(url_for('organizer.post'))
        flash('hey this works')
        return redirect(url_for('organizer.post'))
    return render_template("post.html", title='Post Event', form=form)

# driver 
@mod.route('/user/<string:username>/posts')
@login_required
def user_posts(username):
    posts = current_user.get_all_events()
    return render_template("posts.html", events=posts)

@mod.route('/user/<string:username>/followed')
@login_required
def followed(username):
    followed_events = current_user.followed.all()
    return render_template("followed_events.html", events=followed_events)


# WIP
@mod.route('/user/<string:username>/about')
@login_required
def about(username):
    user = {
        'username': username,
        'about': 'This is an example About Me section.',
        'img_file': url_for('static', filename='profile_pics/default.jpg'),
        'interests': [
            'Computer Science',
            'Sports',
            'Basketball',
            'Movies'
        ]
    }
    info = {}
    return render_template('about.html', user=user, info=info)