from flask import Blueprint, render_template, request, session, url_for, redirect, flash, current_app
from werkzeug.urls import url_parse
from app.models import User, Event
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

@mod.route('/search')
@login_required
def search():
    form = SearchForm()
    if not form.validate():
        return render_template('search.html', title='Search', form=form)
    page = request.args.get('page', 1, type=int)
    posts, total = Event.search(form.q.data, page, current_app.config['EVENTS_PER_PAGE'])
    next_url = url_for('home.search', q=form.q.data, page=page + 1) \
        if total > page * current_app.config['EVENTS_PER_PAGE'] else None
    prev_url = url_for('home.search', q=form.q.data, page=page - 1) \
        if page > 1 else None

    return render_template('results.html', title='Search Results', events=events,
                            next_url=next_url, prev_url=prev_url)
    
