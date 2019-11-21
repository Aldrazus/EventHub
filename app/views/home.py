from flask import Blueprint, render_template, request, session, url_for, redirect, flash, current_app
from werkzeug.urls import url_parse
from app.models import User, Event, EventActivity, Notification, UserActivity, friends
from app.search import search as sch
from flask_login import current_user, login_user, logout_user, login_required
from app import db
from forms import SearchForm, SearchUserForm
from calendar_insert import CalendarInsert 
import config



maps_embeds = {
    'College of Arts & Science': 'https://www.google.com/maps/embed/v1/place?q=NYU%20College%20of%20Arts%20%26%20Science&key=AIzaSyCE8f0oQgzYBUSbvagVTcODMm9I_s_Nkds',
    'College of Dentistry': 'https://www.google.com/maps/embed/v1/place?q=place_id:ChIJTfEpmAtZwokRlIHMm0Px9-0&key=AIzaSyCE8f0oQgzYBUSbvagVTcODMm9I_s_Nkds',
    'Gallatin School of Individualized Study': 'https://www.google.com/maps/embed/v1/place?q=place_id:ChIJs95OiZpZwokRDfKpwwdn4Bo&key=AIzaSyCE8f0oQgzYBUSbvagVTcODMm9I_s_Nkds',
    'Leonard N. Stern School of Business': 'https://www.google.com/maps/embed/v1/place?q=place_id:ChIJ5RN4QZBZwokRVkTrcALQKjs&key=AIzaSyCE8f0oQgzYBUSbvagVTcODMm9I_s_Nkds',
    'Liberal Studies': 'https://www.google.com/maps/embed/v1/place?q=place_id:ChIJ0zSnzZlZwokRZB_CTc2_k-M&key=AIzaSyCE8f0oQgzYBUSbvagVTcODMm9I_s_Nkds',
    'Rory Meyers College of Nursing': 'https://www.google.com/maps/embed/v1/place?q=place_id:ChIJZcYM8QtZwokRhgay2nKGjn0&key=AIzaSyCE8f0oQgzYBUSbvagVTcODMm9I_s_Nkds',
    'Steinhardt School of Culture, Education, and Human Development': 'https://www.google.com/maps/embed/v1/place?q=place_id:ChIJ-80gbZxZwokRmbsALjKCZIo&key=AIzaSyCE8f0oQgzYBUSbvagVTcODMm9I_s_Nkds',
    'Silver School of Social Work': 'https://www.google.com/maps/embed/v1/place?q=place_id:ChIJk5usl5BZwokRBa_YxvXx4G0&key=AIzaSyCE8f0oQgzYBUSbvagVTcODMm9I_s_Nkds',
    'School of Professional Studies': 'https://www.google.com/maps/embed/v1/place?q=place_id:ChIJ92Ka15hZwokReVs-5x6Mlrs&key=AIzaSyCE8f0oQgzYBUSbvagVTcODMm9I_s_Nkds',
    'Tandon School of Engineering': 'https://www.google.com/maps/embed/v1/place?q=place_id:ChIJ85aDTUpawokR95FkWT0xm9o&key=AIzaSyCE8f0oQgzYBUSbvagVTcODMm9I_s_Nkds',
    'Tisch School of the Arts': 'https://www.google.com/maps/embed/v1/place?q=place_id:ChIJ0zSnzZlZwokRZB_CTc2_k-M&key=AIzaSyCE8f0oQgzYBUSbvagVTcODMm9I_s_Nkds',
}

mod = Blueprint('home', __name__,
                        template_folder='app/templates')

#   Home Route
@mod.route('/home')
@login_required
def index():
    # Get friends
    user_friends = db.session.query(friends).filter(friends.c.friender_id==current_user.id).all()
    user_friends = [i[1] for i in user_friends]
    # Get Friend Activity
    user_activity = db.session.query(User, UserActivity).filter(
        User.id == UserActivity.user_id, User.id.in_(user_friends)
    ).order_by(UserActivity.time.desc())
    return render_template("home.html", title="Home", user_activity=user_activity)

#   Event Feed Route
@mod.route('/event_feed')
@login_required
def event_feed():
    event_activity = db.session.query(Event, EventActivity).filter(
        Event.id == EventActivity.event_id, EventActivity.verb=="was created"
    ).order_by(EventActivity.time.desc())
    return render_template("event_feed.html", title="Events", event_activity=event_activity )

#   Global User Feed Route
@mod.route('/global/user')
@login_required
def global_user_feed():
    user_activity = db.session.query(User, UserActivity).filter(
        User.id == UserActivity.user_id
    ).order_by(UserActivity.time.desc())
    return render_template("global-user.html", title="Global", user_activity=user_activity)

#   Global Event Feed Route - Likely won't finish
@mod.route('/global/event')
@login_required
def global_event_feed():
    return redirect(url_for('home.home'))

#   Search Route
#   TODO: ADD BACK PAGES
@mod.route('/search')
@login_required
def search():
    form = SearchForm()
    if not form.validate():
        return render_template('search.html', title='Search', form=form)
    time = form.time.data if form.time.data != '' else None
    loc = form.location.data if form.location.data != '' else None
    events, total = sch(Event, form.q.data, loc, time)

    return render_template('results.html', title='Search Results', events=events)

#   Search/Find User Route
@mod.route('/search_user')
@login_required
def search_user():
    form = SearchUserForm()
    if not form.validate():
        return render_template('search-user.html', title='Search', form=form)
    users, total = sch(User, form.q.data)

    return render_template('results-user.html', title='Search Results', users=users)

#   Event Info Route
@mod.route('/event/<event_id>')
@login_required
def event_info(event_id):
    #get event info
    event = Event.query.filter_by(id=event_id).first()
    #check if event exists
    if event is None:
        flash('Event {} - {} not found.'.format(event_id, event.event_name))
        return redirect(url_for('auth.index'))
    
    #check if current user has not viewed event, if not, add view
    if not current_user.has_viewed(event):
        current_user.view(event)

    db.session.commit()

    embed = maps_embeds[event.location]

    return render_template('event-info.html', title='Event Info', event=event, embed=embed)

#   Event Calendar Insert Route
@mod.route('/calendar_insert/<event_id>')
@login_required
def calendar_insert(event_id):
    #get event info
    event = Event.query.filter_by(id=event_id).first()
    #check if event exists
    if event is None:
        flash('Event {} - {} not found.'.format(event_id, event.event_name))
        return redirect(url_for('auth.index'))

    CalendarInsert(event.event_name, event.location, event.description, event.start_time, event.end_time)
    flash('Added to Google Calendar: {}'.format(event.event_name))

    #next_page functionality sourced from:
    #https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('auth.index')
    return redirect(next_page)


#   Follow Event Route
@mod.route('/follow/<event_id>')
@login_required
def follow(event_id):
    #get event to be followed
    event = Event.query.filter_by(id=event_id).first()
    #check if event exists
    if event is None:
        flash('Event {} - {} not found.'.format(event_id, event.event_name))
        return redirect(url_for('auth.index'))
    #make user follow event
    current_user.follow(event)

    db.session.commit()
    activity = UserActivity(
            user_id = current_user.id,
            receiver_id = event.id,
            type = "event",
            verb = "followed",
            info = ""
        )

    db.session.add(activity)

    db.session.commit()
    flash('You are following this event: {}'.format(event.event_name))

    #next_page functionality sourced from:
    #https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('auth.index')
    return redirect(next_page)


#   Unfollow Route
@mod.route('/unfollow/<event_id>')
@login_required
def unfollow(event_id):
    #get event to be unfollowed
    event = Event.query.filter_by(id=event_id).first()
    #check if event exists
    if event is None:
        flash('Event {} - {} not found.'.format(event_id, event.event_name))
        return redirect(url_for('auth.index'))
    #make user unfollow event
    current_user.unfollow(event)
    db.session.commit()
    flash('You have unfollowed this event: {}'.format(event.event_name))
    #next_page functionality sourced from:
    #https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('auth.index')
    return redirect(next_page)

#   Friend User Route
@mod.route('/friend/<user_id>')
@login_required
def friend(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        flash('User {} not found.'.format(user_id))
        return redirect(url_for('auth.index'))
    if user == current_user:
        flash('Cannot friend yourself!')
        return redirect(url_for('auth.index'))
        
    current_user.friend(user)
    db.session.commit()
    flash('You have friended {}'.format(user.username))
    #next_page functionality sourced from:
    #https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('auth.index')
    return redirect(next_page)

#   Unfriend User Route
@mod.route('/unfriend/<user_id>')
@login_required
def unfriend(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        flash('User {} not found.'.format(user_id))
        return redirect(url_for('auth.index'))
    current_user.unfriend(user)
    db.session.commit()
    flash('You have unfriended {}'.format(user.username))
    #next_page functionality sourced from:
    #https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('auth.index')
    return redirect(next_page)

#   RSVP Route
@mod.route('/rsvp/<event_id>')
@login_required
def rsvp_event(event_id):
    #get event to be RSVP'd
    event = Event.query.filter_by(id=event_id).first()
    #check if event exists
    if event is None:
        flash('Event {} - {} not found.'.format(event_id, event.event_name))
        return redirect(url_for('auth.index'))
    #make user RSVP for event
    current_user.rsvp(event)
    db.session.commit()
    flash('You have RSVP\'d this event: {}'.format(event.event_name))
    return redirect(url_for('home.event_info', event_id=event_id))

#   Notifications Route
@mod.route('/notifications')
@login_required
def notifications():
    #get all notifications
    notifs = current_user.notifications.order_by(Notification.timestamp.asc())
    return render_template('notifs.html', title='Notifications', notifs=notifs)
