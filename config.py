import os

#some code from Miguel Grinberg's blog 
#https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database
basedir = os.path.abspath(os.path.dirname(__file__)) #change this later

#config class for flask app
class Config():
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'averybadsecretkey'
    DEBUG = True

    #sqalchemy stuff
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False #lots of overhead and deprecated

    #mysql server stuff (might not use)
    DB_HOST = os.environ.get('HOST') or 'localhost'
    DB_USER = os.environ.get('USER') or 'root'
    DB_PASSWORD = os.environ.get('PASSWORD') or 'password'
    DB_NAME = os.environ.get('NAME') or 'event_hub'

    #search engine stuff
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')

    #events per page
    EVENTS_PER_PAGE = 5