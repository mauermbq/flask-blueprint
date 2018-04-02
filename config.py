"""
Config items of the app, use env variables in context with docker.
It's easy to create an application instance that uses different
configuration simply by passing a new class to the factory function.
"""
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
# read environment variables from env file
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    """use a class to store configuration variables in extensible way"""
    #  cryptographic key usuful when generating signatures or tokens
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    POSTS_PER_PAGE = 25
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MS_TRANSLATOR_KEY = os.environ.get('MS_TRANSLATOR_KEY')
    ADMINS = ['your-email@example.com']
    LANGUAGES = ['de', 'en']
