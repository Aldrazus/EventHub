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
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('auth.index')
        return redirect(next_page)
    return render_template("login.html", title='Sign In', form=form)

@mod.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@mod.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect('/')
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, role=form.role.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('successful registration')
        return redirect(url_for('auth.login'))
    return render_template('register.html', title="Register", form=form)

@mod.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    return render_template('settings.html')

@mod.route('/user/<string:username>', methods=['GET'])
@login_required
def user(username):
    # Get info from db based on username, send to template
    user_info = {
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
    # 10 most recent events, with option to show more potentially added later on
    # Should send associated event object to link that in the activity
    activity = ["Registered for event A", "Created event B"]
    return render_template('user.html', title=username, user=user_info, activity=activity)