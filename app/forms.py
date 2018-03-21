"""
Core container of WTForms. Forms represent a collection of fields, which can
be accessed on the form dictionary-style or attribute style. Every field has a
Widget instance. The widget’s job is rendering an HTML representation of that field.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User


class LoginForm(FlaskForm):
    """Standard Login Form"""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    """
    Registration form of the app

    The class uses stock validator for the input that comes with WTForms.
    Email validator matches the structure of an email address. Since this
    is a registration form, it is customary to ask the user to type the
    password two times to reduce the risk of a typo. When you add any methods
    that match the pattern validate_<field_name>, WTForms takes those as custom
    validators and invokes them in addition to the stock validators.
    """
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    @classmethod
    def validate_username(cls, username):
        """validate if user is not already in DB"""
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')
    @classmethod
    def validate_email(cls, email):
        """validate if email is not already in DB"""
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
