from flask import Blueprint, render_template, request, session, url_for, redirect, flash, current_app
from werkzeug.urls import url_parse
from app.models import User, Event, Notification
from flask_login import current_user, login_user, logout_user, login_required
from app import db
from forms import SearchForm
import config


mod = Blueprint('home', __name__,
                        template_folder='app/templates')

@mod.route('/')
@login_required
def index():
    return 'index page'

#   Search Route
@mod.route('/search')
@login_required
def search():
    form = SearchForm()
    if not form.validate():
        return render_template('search.html', title='Search', form=form)
    page = request.args.get('page', 1, type=int) #get page number being displayed
    events, total = Event.search(form.q.data, page, current_app.config['EVENTS_PER_PAGE'])

    #TODO: remove, not used
    #get url for next page of search results
    next_url = url_for('home.search', q=form.q.data, page=page + 1) \
        if total > page * current_app.config['EVENTS_PER_PAGE'] else None
    #get url for prev page of search results
    prev_url = url_for('home.search', q=form.q.data, page=page - 1) \
        if page > 1 else None

    return render_template('results.html', title='Search Results', events=events,
                            next_url=next_url, prev_url=prev_url)
    

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
    return render_template('event-info.html', title='Event Info', event=event)

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


#   Notifications Route
@mod.route('/notifications')
@login_required
def notifications():
    #get all notifications
    notifs = current_user.notifications.order_by(Notification.timestamp.asc())
    return render_template('notifs.html', title='Notifications', notifs=notifs)
