from flask_login import UserMixin
from app import login_manager, db
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from time import time
from datetime import datetime


#   Many to many association table for user following events
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'))
)

#   Many to many association table for users friending other users
friends = db.Table('friends',
    db.Column('friender_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('friended_id', db.Integer, db.ForeignKey('user.id')),
)

#   Many to many association table for users RSVPing for events
rsvps = db.Table('rsvps',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'))
)

#   Many to many association table for users viewing events
views = db.Table('views',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'))
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
    # Display email on profile?
    private = db.Column(db.Boolean, default=False)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    role = db.Column(db.String(64))
    about = db.Column(db.String(256))
    interests = db.Column(db.String(256))
    # img_file data is created serverside and does not need to be unique
    img_file = db.Column(db.String(128), unique=False, default="default.jpg")

    #   ------------------
    #   USER RELATIONSHIPS
    #   ------------------

    #   Followed Relationship - many to many relationship between followers (users) and
    #       events
    followed = db.relationship(
        'Event', secondary=followers,
        backref=db.backref('followers',lazy='dynamic'), lazy='dynamic'
    )

    #   Owned Events Relationship - one to many relationship between event owner/creator (user)
    #       and events
    events = db.relationship('Event', backref='owner', lazy='dynamic')

    #   Notifications Relationship - one to many relationship between user and notification
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')

    #   RSVP Relationship - many to many relationship between users and events
    rsvped = db.relationship(
        'Event', secondary=rsvps,
        backref=db.backref('rsvpers', lazy='dynamic'), lazy='dynamic'
    )

    #   Viewed Relationship - many to many relationship between users and events
    viewed = db.relationship(
        'Event', secondary=views,
        backref=db.backref('viewers', lazy='dynamic'), lazy='dynamic'
    )

    #   Friended Relationship - many to many relationship between users
    friended = db.relationship(
        'User', secondary=friends,
        #used to remove foreign key ambiguity error
        primaryjoin=(friends.c.friender_id == id),
        secondaryjoin=(friends.c.friended_id == id),
        backref=db.backref('friends', lazy='dynamic'), lazy='dynamic'
    )

    #   -------------
    #   CLASS METHODS
    #   -------------

    #   Friend Methods

    #   Returns True if this user has friended the given user.
    def has_friended(self, user):
        return self.friended.filter(friends.c.friended_id == user.id).count() > 0

    #   Returns True if this user has friended the given user and the user has friended this user.
    def is_friends_with(self, user):
        return self.has_friended(user) and user.has_friended(self)

    #   Makes this user friend the given user, adding an entry to the relationship table
    #       if it doesn't already exist.
    def friend(self, user):
        if not self.has_friended(user):
            self.friended.append(user)
            if not user.has_friended(self):
                category = 'request'
                description = "{} has sent you a friend request!".format(self.username)
                user.add_notification(self.id, category, description)
    
    #   Makes this user unfriend the given user, deleting an entry in the relationship table
    #       only if the entry exists.
    def unfriend(self, user):
        if self.has_friended(user):
            self.friended.remove(user)
        if user.has_friended(self):
            user.friended.remove(self)


    #   Notification Methods

    #   Creates a notification for this user containing provided fields.
    def add_notification(self, sender_id, category, description):
        notif = Notification(category=category, sender_id=sender_id, description=description, read=0, user=self)
        db.session.add(notif)

    #   Sends notifications to every friend of this user. Used after this user posts a new event.
    def notify_friends(self, event):
        for user in self.friended:
            if self.is_friends_with(user):
                category = 'post'
                description = "{} posted a new event: {}".format(self.username, event.event_name)
                user.add_notification(event.id, category, description)


    #   Follow Methods

    #   Returns True if this user is following the given event.
    def is_following(self, event):
        return self.followed.filter(followers.c.event_id == event.id).count() > 0
    
    #   Makes this user follow an event if not already followed.
    def follow(self, event):
        if not self.is_following(event):
            self.followed.append(event)

    #   Makes this user unfollow an event only if they are already following.
    def unfollow(self, event):
        if self.is_following(event):
            self.followed.remove(event)

    #   View Methods

    #   Returns True if this user has viewed the given event.
    def has_viewed(self, event):
        return self.viewed.filter(views.c.event_id == event.id).count() > 0

    #   Makes this user view an event if they haven't already.
    def view(self, event):
        if not self.has_viewed(event):
            self.viewed.append(event)

    #   RSVP Methods

    #   Returns True if this user has RSVP'd for the given event.
    def has_rsvped(self, event):
        return self.rsvped.filter(rsvps.c.event_id == event.id).count() > 0

    #   Makes this user RSVP for an event if they haven't already.
    def rsvp(self, event):
        if not self.has_rsvped(event):
            self.rsvped.append(event)


    #   Query Methods

    #   Returns collection of events this user follows.
    def get_followed_events(self):
        return self.followed

    #   Returns a collection of events this user has posted.
    def get_all_events(self):
        all_events = Event.query.filter_by(owner_id=self.id).all()
        return all_events
    
    
    #   Authentication Methods

    #   Stores hashed password
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    #   Returns True if the hash of the given password matches this user's password hash.
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
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(120), index=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    description = db.Column(db.String(120))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    location = db.Column(db.String(128))   
    # content = db.Column(db.Text())


    #   -------------
    #   CLASS METHODS
    #   -------------

    #   Returns user that created this Event.
    def get_creator(self):
        return User.query.filter_by(id=self.owner_id).first()

    #   Sends notification to all users that follow this event.
    def notify_followers(self):
        creator = self.get_creator()
        for user in self.followers:
            category = 'update'
            description = "{} has updated an event you are following: {}".format(creator.username, self.event_name)
            user.add_notification(self.id, category, description)

    #   Returns view count.
    def get_view_count(self):
        return self.viewers.count()

    #   Returns number of users that RSVP'd for this event.
    def get_rsvp_count(self):
        return self.rsvpers.count()


class EventStats(UserMixin, db.Model):
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), primary_key=True)

class UserActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True) # activity id
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # Who receives the action (if any) (e.g. user follows ->event)
    receiver_id = db.Column(db.Integer)
    # What is the receiver (event, user)
    type = db.Column(db.String(32))
    # What is the action (create, follow, update)
    verb = db.Column(db.String(32))
    # Extra info if useful and can avoid a join
    info = db.Column(db.String(255))
    # When did it happen
    time = db.Column(db.DateTime, default=datetime.now())
    
class EventActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True) # activity id
    event_id = db.Column(db.Integer)
    # Who receives the action (if any) (e.g. event posts notification)
    receiver_id = db.Column(db.Integer)
    # What is the receiver (event, user)
    type = db.Column(db.String(32))
    # What is the action (create, follow, update)
    verb = db.Column(db.String(32))
    # Extra info if useful and can avoid a join
    info = db.Column(db.String(255))
    # When did it happen
    time = db.Column(db.DateTime, default=datetime.now())

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #type field maybe? can be create, update, etc.
    category = db.Column(db.String(120))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sender_id = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now())
    description = db.Column(db.Text)
    read = db.Column(db.Integer) #unread = 0, read = 1
    #link to user/event profile depending on type.
    #link = db.Column(db.String(120)) #link to event page or friend request or something
    


#   Callback function used to reload the user object from the user ID stored in the session.
#   For more info & source of this function: https://flask-login.readthedocs.io/en/latest/#your-user-class
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

