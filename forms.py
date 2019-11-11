from flask import request
from flask_wtf import FlaskForm
#from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SubmitField, RadioField, TextAreaField
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Required, regexp
from app.models import User
import re

#login form used in login page (users)
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    role = RadioField('Role', choices=[
        ('Student', 'Student'),
        ('Event Organizer', 'Event Organizer')],
        default='Student', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username unavailable.')

class PostForm(FlaskForm):
    event_name = StringField('Event Name', validators=[DataRequired()])
    event_desc = TextAreaField('Event Description')

    #code from https://flask-wtf.readthedocs.io/en/latest/form.html#module-flask_wtf.file
    #image = FileField('Image File', validators=[
    #    FileRequired('hey this is required'),
    #    FileAllowed(['jpg', 'png'], 'Images only')
    #])

    location = StringField('Location', validators=[DataRequired()])
    #start = StringField('Start Time', validators=[DataRequired()])
    start = DateTimeLocalField('Start Time', format='%Y-%m-%dT%H:%M')
    end = DateTimeLocalField('End Time', format='%Y-%m-%dT%H:%M')
    submit = SubmitField('Post Event')

class SearchForm(FlaskForm):
    q = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)

class SearchUserForm(FlaskForm):
    q = StringField('Search User', validators=[DataRequired()])
    submit = SubmitField('Search')

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchUserForm, self).__init__(*args, **kwargs)