from flask import Flask
from config import Config

app = Flask(__name__)
#apply config class to app.config
app.config.from_object(Config)

#import router packages containing blueprints
from app.views import login

#register blueprints to flask app
app.register_blueprint(login.mod)