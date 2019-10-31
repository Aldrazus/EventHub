from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

#setting up flask app with config
app = Flask(__name__)
app.config.from_object(Config)

#sqlalchemy db
db = SQLAlchemy(app)
migrate = Migrate(app, db)


#login manager
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

#import router packages containing blueprints
from app.views import auth, organizer

#import models
from app import models

#register blueprints to flask app
app.register_blueprint(auth.mod)
app.register_blueprint(organizer.mod)