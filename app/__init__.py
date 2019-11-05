from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from elasticsearch import Elasticsearch
from flask_moment import Moment
from config import Config


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
moment = Moment()

def create_app(config_cls=Config, testing=False):
    #setting up flask app with config
    app = Flask(__name__)
    app.config.from_object(config_cls)

    if testing:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'

    #sqlalchemy db
    db.init_app(app)
    migrate.init_app(app, db)

    #login manager
    login_manager.init_app(app)

    #moment
    moment.init_app(app)


    #import router packages containing blueprints
    from app.views import auth, organizer, home

    #import models
    from app import models
    
    #register blueprints to flask app
    app.register_blueprint(auth.mod)
    app.register_blueprint(organizer.mod)
    app.register_blueprint(home.mod)

    #search engine
    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
        if app.config['ELASTICSEARCH_URL'] else None

    return app



