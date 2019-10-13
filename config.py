import os

SECRET_KEY = os.environ.get('SECRET_KEY') or 'averybadsecretkey'
DEBUG = True
DB_HOST = os.environ.get('HOST') or 'localhost'
DB_USER = os.environ.get('USER') or 'root'
DB_PASSWORD = os.environ.get('PASSWORD') or 'password'
DB_NAME = os.environ.get('NAME') or 'event_hub'
    
