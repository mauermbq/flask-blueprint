"""
Initialize app as application module.
Import the view module after the application object is created.
When a blueprint is registered, any view functions, templates, static files,
error handlers, etc. are connected to the application.
Optional rl_prefix: attach a blueprint under a URL prefix. It keeps all the
routes in the blueprint separated from other routes in the application  "namespacing".
"""
# Flask uses Python's logging package to write its logs

import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _l
from flask import Flask, request, current_app
from config import Config

# create extension instances, will be initialized later in the Factory method
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = _l('Please log in to access this page.')
mail = Mail()
bootstrap = Bootstrap()
moment = Moment()
babel = Babel()

def create_app(config_class=Config):
    """constructs a Flask application instance"""
    # create flask application object and all required extensions
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    babel.init_app(app)
    # register error blueprint
    # put the import of the blueprint right above the app.register_blueprint()
    # to avoid circular dependencies.
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)
    # register auth blueprint
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    # register main blueprint
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    # add SMTPHandler instance to the Flask logger object, which is app.logger
    # all this logging is skipped during unit tests.
    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'],
                        app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='Microblog Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/microblog.log',
                                           maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Microblog startup')
    return app

# localeselector decorator is invoked for each request to get language
@babel.localeselector
def get_locale():
    """
    accept_languages object provides a interface to work with the Accept-Language header.
    (see https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Accept-Language)
    The contents of this header can be configured in the browser's preferences page, with
    the default being usually imported from the language settings in the computer's operating
    system. best_match ompare the list of languages requested by the client against the
    languages the application supports, and using the client provided weights.
    """
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])

# avoid circular import
# pylint: disable=C0413
from app import models
