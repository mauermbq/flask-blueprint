from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
### force user to login ###
# If a user who is not logged in tries to view a protected page, Flask-Login 
# will automatically redirect the user to the login form where @login_required
login.login_view = 'login'

from app import routes, models
