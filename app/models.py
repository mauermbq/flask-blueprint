"""
Definition of App models. The baseclass for all your models is called db.Model.
It’s stored on the SQLAlchemy instance you have to create.
To override the table name, set the __tablename__ class attribute.
"""
from datetime import datetime
from time import time
from hashlib import md5
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_babel import lazy_gettext as _l
from flask import current_app
from app import db, login

# auxiliary table that has no data other than the foreign keys withoud model Class
followers = db.Table('followers',
                     db.Column('follower_id', db.Integer,
                               db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id')))

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
    other requirements. Consequently it is db agnostic.
    Use db.relationship function to define the relationship in the model class.
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
        db Model, instance of SQLAlchemy obeject (hint: some linters have problems with it)
    """

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def avatar(self, size):
        """
        Returns the URL of the user's avatar image, scaled to the requested size in pixels.
        Gravatar doc: https://de.gravatar.com/site/implement/images
        For users that don't have an avatar registered, an "identicon" image will be generated.
        """
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def set_password(self, password):
        """store password as hash"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """return true if password matches hashed value"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def followed_posts(self):
        """
        invoking the join operation on the posts table and put it a temporary table that
        combines data from posts and followers tables.
        It filters the users of interest and sort it by post timestamp and include the user's
        own posts through a union.
        Hint: The "c" is an attribute of SQLAlchemy tables that are not defined as models.
        For these tables, the table columns are all exposed as sub-attributes of this "c" attribute.
        """
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def follow(self, user):
        """append follower"""
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        """unfollow uswer"""
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        """check is user is following"""
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def get_reset_password_token(self, expires_in=600):
        """
        Create JWT token for password reset belongin to the User. Decode('utf-8') is necessary
        because the jwt.encode() function returns the token as a byte sequence
        Returns
        -------
        str
            generated JWT token as a string
        """
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        """
        takes a token and attempts to decode it by invoking PyJWT's jwt.decode() function
        """
        try:
            uid = jwt.decode(token, current_app.config['SECRET_KEY'],
                             algorithms=['HS256'])['reset_password']
        except jwt.ExpiredSignatureError:
            return _l("Token has expired")
        return User.query.get(uid)

    # declare the many-to-many relationship
    # primaryjoin indicates the condition that links the left side entity
    # secondaryjoin indicates the condition that links the right side entity
    # backref define how relationship will be accessed from the right side entity
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

class Post(db.Model):
    """schema for storing posts"""
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    language = db.Column(db.String(5))

    def __repr__(self):
        return '<Post {}>'.format(self.body)
