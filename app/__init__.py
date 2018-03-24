"""
Initialize app as application module.
Import the view module after the application object is created.
"""
# Flask uses Python's logging package to write its logs
import os
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask import Flask
from config import Config

# create flask application object
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

### force user to login ###
# If a user who is not logged in tries to view a protected page, Flask-Login
# will automatically redirect the user to the login form where @login_required
login.login_view = 'login'

# add SMTPHandler instance to the Flask logger object, which is app.logger
if not app.debug:
    if app.config['MAIL_SERVER']:
        AUTH = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            AUTH = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        SECURE = None
        if app.config['MAIL_USE_TLS']:
            SECURE = ()
        MAIL_HANDLER = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='Microblog Failure',
            credentials=AUTH, secure=SECURE)
        MAIL_HANDLER.setLevel(logging.ERROR)
        app.logger.addHandler(MAIL_HANDLER)
    # rotating file handler
    if not os.path.exists('logs'):
        os.mkdir('logs')
    FILE_HANDLER = RotatingFileHandler('logs/microblog.log', maxBytes=10240, backupCount=10)
    FILE_HANDLER.setFormatter(
        logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    FILE_HANDLER.setLevel(logging.INFO)
    app.logger.addHandler(FILE_HANDLER)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Microblog startup')

from app import routes, models, errors
