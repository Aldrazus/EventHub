from flask import Blueprint, render_template, request, session, url_for, redirect, flash, current_app
from werkzeug.urls import url_parse
from app.models import User, UserActivity
from flask_login import current_user, login_user, logout_user, login_required
from forms import LoginForm, RegisterForm, AccountSettingsForm
from app import db
from PIL import Image
import config
import os


mod = Blueprint('auth', __name__,
                        template_folder='app/templates')


#some code from Miguel Grinberg's blog
#https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
@mod.route('/')
@login_required
def index():
    return redirect(url_for('home.index'))

#   Login Route
@mod.route('/login', methods=['GET', 'POST'])
def login():
    #redirect to home page if user already logged in
    if current_user.is_authenticated:
        return redirect('/')
    
    form = LoginForm()
    if form.validate_on_submit():
        #check if user exists and passwords match
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user)

        #next_page functionality sourced from:
        #https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('auth.index')
        return redirect(next_page)
    return render_template("login.html", title='Sign In', form=form)

#   Logout Route
@mod.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

#   Register Route
@mod.route('/register', methods=['GET', 'POST'])
def register():
    #redirect user if already logged in
    if current_user.is_authenticated:
        return redirect('/')
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data, 
            role=form.role.data,
            email=form.email.data,
            )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()
        activity = UserActivity(
            user_id = user.id,
            type = "user",
            verb = "registered",
        )

        db.session.add(activity)

        db.session.commit()

        flash('successful registration')
        return redirect(url_for('auth.login'))
    return render_template('register.html', title="Register", form=form)

def save_picture(form_picture):
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = str(current_user.id) + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)
    output_size = (250, 250)
    img = Image.open(form_picture)
    # thumbnail works better than resize
    img.thumbnail(output_size)
    img.save(picture_path)
    # By overwriting the file to have the same path, the old image is still 
    # cached, but using a new path will require changes to make sure old
    # profile pictures will get deleted
    return picture_fn

@mod.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = AccountSettingsForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.img_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.about = form.about.data
        current_user.interests = form.interests.data
        current_user.private = form.private.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('auth.settings'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.private.data = current_user.private
        form.about.data = current_user.about
        form.interests.data = current_user.interests
    return render_template('settings.html', title='Settings', form=form)

# Should move this to a user blueprint
@mod.route('/profile/<string:username>', methods=['GET'])
@login_required
def profile(username):
    # Get info from db based on username, send to template
    if username == current_user.username:
        user = current_user
    else:
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))

    # Some recent events, with option to show more potentially added later on
    # Should send associated event object to link that in the activity
    
    # activity = ["Registered for event A", "Created event B"]

    activity = UserActivity.query.filter_by(
        user_id=user.id
        ).order_by(
            UserActivity.time.desc()
            ).limit(10)

    return render_template('profile.html', title=username, user=user, activity=activity)