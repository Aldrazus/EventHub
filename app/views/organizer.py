from flask import Blueprint, render_template, request, session, url_for, redirect, flash
from werkzeug.urls import url_parse
from app.models import User, Event, UserActivity, EventActivity
from flask_login import current_user, login_user, logout_user, login_required
from forms import PostForm, UpdateEventForm
from app import db
import config


mod = Blueprint('organizer', __name__,
                        template_folder='app/templates')

#   Home/Index Route
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
        event = Event(
            event_name=form.event_name.data, 
            owner_id=current_user.id, 
            description=form.event_desc.data, 
            start_time=form.start.data, 
            end_time=form.end.data, 
            location=form.location.data
        )
        # 
        db.session.add(event)
        db.session.flush()

        user_action = UserActivity(
            user_id = current_user.id,
            receiver_id = event.id,
            type = "event",
            verb = "created",
            info = ""
        )

        event_action = EventActivity(
            event_id = event.id,
            receiver_id = event.id,
            type = "event",
            verb = "was created",
            info = ""
        )

        db.session.add(user_action)
        db.session.add(event_action)

        current_user.notify_friends(event)
        db.session.commit()

        if False: #TODO: do some checks on the form
            flash('Invalid data')
            return redirect(url_for('organizer.post'))
        flash('You have posted a new event: {}'.format(event.event_name))
    return render_template("post.html", title='Post Event', form=form)

@mod.route('/update/<event_id>', methods=['GET', 'POST'])
@login_required
def update(event_id):
    #get event
    event = Event.query.filter_by(id=event_id).first()
    #check if event exists
    if event is None:
        flash('Event {} - {} not found.'.format(event_id, event.event_name))
        return redirect(url_for('auth.index'))
    
    form = UpdateEventForm()
    if form.validate_on_submit():
        event.event_name = form.event_name.data 
        event.description = form.event_desc.data
        event.start_time = form.start.data
        event.end_time = form.end.data
        event.location = form.location.data
        event.notify_followers()
        db.session.commit()
        flash('You have updated your event: {}'.format(event.event_name))
        return redirect(url_for('home.event_info', event_id=event.id))
    return render_template("update.html", title='Update Event', form=form, event_id=event_id)


# User Posts Route (rename to events?)
@mod.route('/profile/<string:username>/posts')
@login_required
def user_posts(username):
    #get user and events made by user
    user = User.query.filter_by(username=username).first()
    posts = user.get_all_events() #rename to events?
    return render_template("posts.html", user=user, events=posts)

#   Followed Events Route
@mod.route('/profile/<string:username>/followed')
@login_required
def followed(username):
    #TODO: check if user is not current_user, else dont make query
    user = User.query.filter_by(username=username).first()
    followed_events = user.get_followed_events()
    return render_template("followed_events.html", user=user, events=followed_events) #rename this to something better like event_info


#   About User Route
@mod.route('/profile/<string:username>/about')
@login_required
def about(username):
    user = User.query.filter_by(username=username).first()
    friends = user.friended
    return render_template('about.html', user=user, friends=friends)