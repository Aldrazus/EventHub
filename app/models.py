from flask_login import UserMixin
from app import login_manager, db
from werkzeug.security import generate_password_hash, check_password_hash
from time import time

#many to many association table for user following events
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'))
)

#many to many association table for users friending other users
#use this maybe:
#https://stackoverflow.com/questions/9116924/how-can-i-achieve-a-self-referencing-many-to-many-relationship-on-the-sqlalchemy
friends = db.Table('friends',
    db.Column('friender_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('friended_id', db.Integer, db.ForeignKey('user.id')),
)

#   User Class - model representing app users, can either be 'Student' or 'Event Organizer'
#   Inherits from UserMixin to implement necessary functions for flask-login
#   For more info on UserMixin: https://flask-login.readthedocs.io/en/latest/#your-user-class
#   Inherits from Model class, which is a base for models being stored in database
#   For more info on Models: https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/#a-minimal-application
class User(UserMixin, db.Model):
    __searchable__ = ['username', 'first_name', 'last_name']
    #columns in user table
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    role = db.Column(db.String(64))
    interests = db.Column(db.Text)

    
    #   Relationships
    #   For more info on relationships: https://docs.sqlalchemy.org/en/13/orm/basic_relationships.html

    #   Followed Relationship - many to many relationship between followers (users) and
    #       events
    #   
    followed = db.relationship(
        'Event', secondary=followers,
        backref=db.backref('followers',lazy='dynamic'), lazy='dynamic'
    )

    #   Owned Events Relationship - one to many relationship between event owner/creator (user)
    #       and events
    events = db.relationship('Event', backref='owner', lazy='dynamic')

    #   Notifications Relationship - one to many relationship between user and notification
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')

    #   Friended Relationship - many to many relationship between users
    friended = db.relationship(
        'User', secondary=friends,
        #used to remove foreign key ambiguity error
        primaryjoin=(friends.c.friender_id == id),
        secondaryjoin=(friends.c.friended_id == id),
        backref=db.backref('friends', lazy='dynamic'), lazy='dynamic'
    )

    #   Some useful functions related to friends

    def has_friended(self, user):
        return self.friended.filter(friends.c.friended_id == user.id).count() > 0

    def is_friends_with(self, user):
        return self.has_friended(user) and user.has_friended(self)

    def friend(self, user):
        if not self.has_friended(user):
            self.friended.append(user)
    
    def unfriend(self, user):
        if self.has_friended(user):
            self.friended.remove(user)
        if user.has_friended(self):
            user.friended.remove(self)






    #   Some useful functions related to follows

    #check if user is following event
    def is_following(self, event):
        return self.followed.filter(followers.c.event_id == event.id).count() > 0
    
    #follow event if not already followed
    def follow(self, event):
        if not self.is_following(event):
            self.followed.append(event)

    #unfollow event if user following event
    def unfollow(self, event):
        if self.is_following(event):
            self.followed.remove(event)


    #   Some useful queries

    #get all events a user is following joined with the creators of those events
    def get_followed_events(self):
        followed_events = db.session.query(User, Event).join(User.followed)
        return followed_events.filter(User.id == self.id)

    #returns tuple of (User, Event) fields. Index 0 for user fields, 1 for event fields
    #TODO: dont return a tuple, just get events and use Event.get_creator() function - done
    def get_all_events(self):
        all_events = Event.query.filter_by(owner_id=self.id).all()
        return all_events
    
    
    #   Some useful functions for registering and authenticating users securely

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


#   Event Class - model representing events posted by organizers
#   Inherits from UserMixin to implement necessary functions for flask-login
#   For more info on UserMixin: https://flask-login.readthedocs.io/en/latest/#your-user-class
#   Inherits from Model class, which is a base for models being stored in database
#   For more info on Models: https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/#a-minimal-application
#   Inherits from Searchable class, which provides indexing functionalities
class Event(UserMixin, db.Model):
    #   Fields that are able to be searched in search engine
    __searchable__ = ['event_name', 'description', 'start_time', 'location'] 

    #columns in user table
    #TODO: include times, location, and keywords as searchables
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(120), index=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    description = db.Column(db.String(120))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    location = db.Column(db.String(128))   
    content = db.Column(db.Text())

    #   Some useful queries

    def get_creator(self):
        return User.query.filter_by(id=self.owner_id).first()


class EventStats(UserMixin, db.Model):
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), primary_key=True)


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #type field maybe? can be create, update, etc.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.Float, index=True, default=time)
    description = db.Column(db.Text)
    #link = db.Column(db.String(120)) #link to event page or friend request or something
    


#   Callback function used to reload the user object from the user ID stored in the session.
#   For more info & source of this function: https://flask-login.readthedocs.io/en/latest/#your-user-class
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

