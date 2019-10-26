from flask import Blueprint, render_template, request, session, url_for, redirect, flash
from werkzeug.urls import url_parse
from app.models import User
from flask_login import current_user, login_user, logout_user, login_required
from forms import LoginForm, RegisterForm
from app import db
import config


mod = Blueprint('auth', __name__,
                        template_folder='app/templates')


#some code from Miguel Grinberg's blog
#https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
@mod.route('/')
@login_required
def index():
    return render_template("home.html", title="Home")

@mod.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user)
        return redirect('/')
    return render_template("login.html", title='Sign In', form=form)

@mod.route('/logout')
def logout():
    logout_user()
    return redirect('/')

@mod.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect('/')
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, role="student")
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('successful registration')
        return redirect(url_for('auth.login'))
    return render_template('register.html', title="Register", form=form)