from flask import Blueprint, render_template, request, session, url_for, redirect, flash
from werkzeug.urls import url_parse
from app.models import User
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

@mod.route('/post')
@login_required
def post():
    form = PostForm()
    if form.validate_on_submit():
        flash('hey this works')
        return redirect(url_for('organizer.post'))
    return render_template("post.html", title='Post Event', form=form)