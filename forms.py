from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField, FileField, TextAreaField
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
        default='Student', validators=[Required()])
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
    image = FileField('Image File', [regexp(u'^[^/\\\]\.jpg$')])
    location = StringField('Location', validators=[DataRequired()])
    start = StringField('Start Time', validators=[DataRequired()])
    end = StringField('End Time', validators=[DataRequired()])
    submit = SubmitField('Post Event')

    def validate_image(self, image):
        if image.data:
            image.data = re.sub(r'[^a-z0-9_.-]', '_', image.data)



    