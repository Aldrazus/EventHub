from flask import Blueprint, render_template, request, session, url_for, redirect, flash
from werkzeug.urls import url_parse
from app.models import User, Event
from flask_login import current_user, login_user, logout_user, login_required
from forms import PostForm
from app import db
import config


mod = Blueprint('organizer', __name__,
                        template_folder='app/templates')


@mod.route('/')
@login_required
def index():
    return render_template("home.html", title="Home")

#   Post Route
@mod.route('/post', methods=['GET', 'POST'])
@login_required
def post():
    form = PostForm()
    if form.validate_on_submit():
        #create new event and store in database
        event = Event(event_name=form.event_name.data, 
            owner_id=current_user.id, 
            description=form.event_desc.data, 
            start_time=form.start.data, 
            end_time=form.end.data, 
            location=form.location.data
        )
        db.session.add(event)
        db.session.commit()

        if False: #TODO: do some checks on the form
            flash('Invalid data')
            return redirect(url_for('organizer.post'))
        flash('hey this works' + str(event.start_time)) #TODO: change this and redirect to more appropriate page
        return redirect(url_for('organizer.post'))
    return render_template("post.html", title='Post Event', form=form)

#   User Posts Route (rename to events?)
@mod.route('/user/<string:username>/posts')
@login_required
def user_posts(username):
    #get user and events made by user
    user = User.query.filter_by(username=username).first()
    posts = user.get_all_events() #rename to events?
    return render_template("posts.html", user=user, events=posts)

#   Followed Events Route
@mod.route('/user/<string:username>/followed')
@login_required
def followed(username):
    #TODO: check if user is not current_user, else dont make query
    user = User.query.filter_by(username=username).first()
    followed_events = user.get_followed_events()
    return render_template("followed_events.html", user=user, events=followed_events) #rename this to something better like event_info


# WIP
#   About Route
@mod.route('/user/<string:username>/about')
@login_required
def about(username):
    user = {
        'username': username,
        'role': 'Event Organizer',
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