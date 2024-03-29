from flask import request
from flask_wtf import FlaskForm
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SubmitField, RadioField, TextAreaField, SelectField, BooleanField
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Required, regexp, Length
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
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username unavailable.')

#   TODO: Add more specific location field (e.g. room)
class PostForm(FlaskForm):
    event_name = StringField('Event Name', validators=[DataRequired()])
    event_desc = TextAreaField('Event Description')

    #code from https://flask-wtf.readthedocs.io/en/latest/form.html#module-flask_wtf.file
    #image = FileField('Image File', validators=[
    #    FileRequired('hey this is required'),
    #    FileAllowed(['jpg', 'png'], 'Images only')
    #])

    location = SelectField('School/College', validators=[DataRequired()], 
	choices=[
	('College of Arts & Science', 'College of Arts & Science'), 
	('College of Dentistry', 'College of Dentistry'), 
	('Gallatin School of Individualized Study', 'Gallatin School of Individualized Study'), 
	('Leonard N. Stern School of Business', 'Leonard N. Stern School of Business'), 
	('Liberal Studies', 'Liberal Studies'), 
	('Rory Meyers College of Nursing', 'Rory Meyers College of Nursing'), 
	('Steinhardt School of Culture, Education, and Human Development', 'Steinhardt School of Culture, Education, and Human Development'), 
	('Silver School of Social Work', 'Silver School of Social Work'), 
	('School of Professional Studies', 'School of Professional Studies'), 
	('Tandon School of Engineering', 'Tandon School of Engineering'), 
	('Tisch School of the Arts', 'Tisch School of the Arts')
	])
    #start = StringField('Start Time', validators=[DataRequired()])
    start = DateTimeLocalField('Start Time', format='%Y-%m-%dT%H:%M')
    end = DateTimeLocalField('End Time', format='%Y-%m-%dT%H:%M')
    submit = SubmitField('Post Event')

class SearchForm(FlaskForm):
    q = StringField('Search', validators=[DataRequired()])
    #add more fields like time and location
    time = SelectField('Time', choices=[
        ('', 'Any'),
        ('today', 'Today'),
        ('week', 'This Week'),
        ('month', 'This Month'),
    ])
    location = SelectField('School/College', choices=[
    ('', 'Any'),
	('College of Arts & Science', 'College of Arts & Science'), 
	('College of Dentistry', 'College of Dentistry'), 
	('Gallatin School of Individualized Study', 'Gallatin School of Individualized Study'), 
	('Leonard N. Stern School of Business', 'Leonard N. Stern School of Business'), 
	('Liberal Studies', 'Liberal Studies'), 
	('Rory Meyers College of Nursing', 'Rory Meyers College of Nursing'), 
	('Steinhardt School of Culture, Education, and Human Development', 'Steinhardt School of Culture, Education, and Human Development'), 
	('Silver School of Social Work', 'Silver School of Social Work'), 
	('School of Professional Studies', 'School of Professional Studies'), 
	('Tandon School of Engineering', 'Tandon School of Engineering'), 
	('Tisch School of the Arts', 'Tisch School of the Arts')
	])
    submit = SubmitField('Search')

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)

class AccountSettingsForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    private = BooleanField('Make Email Private?')
    about = TextAreaField('About', validators=[Length(max=256)])
    interests = TextAreaField('Interests', validators=[Length(max=256)])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')
class SearchUserForm(FlaskForm):
    q = StringField('Search User', validators=[DataRequired()])
    submit = SubmitField('Search')

    #TODO: remove this maybe
    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchUserForm, self).__init__(*args, **kwargs)

class UpdateEventForm(FlaskForm):
    event_name = StringField('Event Name', validators=[DataRequired()])
    event_desc = TextAreaField('Event Description')

    #code from https://flask-wtf.readthedocs.io/en/latest/form.html#module-flask_wtf.file
    #image = FileField('Image File', validators=[
    #    FileRequired('hey this is required'),
    #    FileAllowed(['jpg', 'png'], 'Images only')
    #])

    location = SelectField('School/College', validators=[DataRequired()], 
	choices=[
	('College of Arts & Science', 'College of Arts & Science'), 
	('College of Dentistry', 'College of Dentistry'), 
	('Gallatin School of Individualized Study', 'Gallatin School of Individualized Study'), 
	('Leonard N. Stern School of Business', 'Leonard N. Stern School of Business'), 
	('Liberal Studies', 'Liberal Studies'), 
	('Rory Meyers College of Nursing', 'Rory Meyers College of Nursing'), 
	('Steinhardt School of Culture, Education, and Human Development', 'Steinhardt School of Culture, Education, and Human Development'), 
	('Silver School of Social Work', 'Silver School of Social Work'), 
	('School of Professional Studies', 'School of Professional Studies'), 
	('Tandon School of Engineering', 'Tandon School of Engineering'), 
	('Tisch School of the Arts', 'Tisch School of the Arts')
	])
    #start = StringField('Start Time', validators=[DataRequired()])
    start = DateTimeLocalField('Start Time', format='%Y-%m-%dT%H:%M')
    end = DateTimeLocalField('End Time', format='%Y-%m-%dT%H:%M')
    submit = SubmitField('Update Event')
