from flask import Flask

app = Flask(__name__)

#import router packages containing blueprints
from app.views import login

#register blueprints to flask app
app.register_blueprint(login.mod)