"""Definition of App models"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login


@login.user_loader
def load_user(id_):
    """
    User Loader Function: Flask-Login keeps track of the logged in user by storing
    its unique identifier in Flask's user session. Each time the logged-in user navigates
    to a new page, Flask-Login retrieves the ID of the user from the session. Flask-Login
    knows nothing about databases, and expects that the application will configure a user
    loader function.
    The user loader is registered with Flask-Login via @login.user_loader decorator

    Parameters
    ----------
    id : String
        Flask-Login passes id to the function

    Returns
    -------
    int
        Databases that use numeric IDs need to convert the string to integer
    """
    return User.query.get(int(id_))

class User(UserMixin, db.Model):
    """
    The Flask-Login extension works with the application's user model, and expects
    certain properties and methods to be implemented in it (see below). As long as
    these required items are added to the model, Flask-Login does not have any
    other requirements. Consequently it is DB agnostic.
    Parameters
    ----------
    UserMixin : UserMixin
        Flask-Login provides a mixin class called UserMixin that includes generic
        implementations of:
        * is_authenticated: property is True if the user has valid credentials or False otherwise.
        * is_active: property that is True if the user's account is active or False otherwise.
        * is_anonymous: property that is False for regular users, True for special, anonymous user.
        * get_id(): method that returns a unique identifier for the user as a string
    db.Model : Model
        DB Model, instance of SQLAlchemy obeject (hint: some linters have problems with it)
    """

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def set_password(self, password):
        """store password as hash"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """return true if password matches hashed value"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Post(db.Model):
    """schema for storing posts"""
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)
