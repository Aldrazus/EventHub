from flask_login import UserMixin
from app import login_manager, db
from werkzeug.security import generate_password_hash, check_password_hash

#some code from Miguel Grinberg's blog
#https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
#user model used for testing login
class User(UserMixin, db.Model):
    #columns in user table
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    firstname = db.Column(db.String(64))
    lastname = db.Column(db.String(64))
    role = db.Column(db.String(64))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Event:
    EventID = db.Column(db.Integer, primary_key=True)
    EventName = db.Column(db.String(120), index=True)
    OwnerID = db.Column(db.Integer)
    StartTime = db.Column(db.DateTime)
    EndTime = db.Column(db.DateTime)
    Location = db.Column(db.String(128))    

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

