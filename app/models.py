from flask_login import UserMixin
from app import login_manager, db
from app.search import add_to_index, remove_from_index, query_index
from werkzeug.security import generate_password_hash, check_password_hash

#many to many association table for user following events
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'))
)

#TODO: cite this
class Searchable():

    #TODO: move to Event and User classes
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0

        when = [(ids[i], i) for i in range(len(ids))]
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total
    
    #TODO: remove dictionary, strip down, and move to search
    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    #TODO: move to search
    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, Searchable):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, Searchable):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, Searchable):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None


    #dont need this
    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)

db.event.listen(db.session, 'before_commit', Searchable.before_commit)
db.event.listen(db.session, 'after_commit', Searchable.after_commit)

#   User Class - model representing app users, can either be 'Student' or 'Event Organizer'
#   Inherits from UserMixin to implement necessary functions for flask-login
#   For more info on UserMixin: https://flask-login.readthedocs.io/en/latest/#your-user-class
#   Inherits from Model class, which is a base for models being stored in database
#   For more info on Models: https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/#a-minimal-application
class User(UserMixin, db.Model):
    #columns in user table
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    role = db.Column(db.String(64))

    
    #   Followed Relationship - many to many relationship between followers (users) and
    #       events
    #   For more info on relationships: https://docs.sqlalchemy.org/en/13/orm/basic_relationships.html
    followed = db.relationship(
        'Event', secondary=followers,
        backref=db.backref('followers',lazy='dynamic'), lazy='dynamic'
    )

    #   Owned Events Relationship - one to many relationship between event owner/creator (user)
    #       and events
    #   For more info on relationships: https://docs.sqlalchemy.org/en/13/orm/basic_relationships.html
    events = db.relationship('Event', backref='owner', lazy='dynamic')


    #   Some useful queries

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

    #get all events a user is following joined with the creators of those events
    def get_followed_events(self):
        followed_events = db.session.query(User, Event).join(User.followed)
        return followed_events.filter(User.id == self.id)

    #returns tuple of (User, Event) fields. Index 0 for user fields, 1 for event fields
    #TODO: dont return a tuple, just get events and use Event.get_creator() function
    def get_all_events(self):
        all_events = db.session.query(User, Event).join(Event)
        return all_events.filter_by(id=self.id)
    
    
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
class Event(Searchable, UserMixin, db.Model):
    #   Fields that are able to be searched in search engine
    __searchable__ = ['event_name', 'description'] 

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


#   Callback function used to reload the user object from the user ID stored in the session.
#   For more info & source of this function: https://flask-login.readthedocs.io/en/latest/#your-user-class
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

